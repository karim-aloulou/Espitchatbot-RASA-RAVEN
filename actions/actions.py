import logging,os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from langdetect import detect
from translate import Translator
from rwkv.model import RWKV
from rwkv.utils import PIPELINE, PIPELINE_ARGS
current_path = os.path.dirname(os.path.abspath(__file__))

# set these before import RWKV
os.environ['RWKV_JIT_ON'] = '1'
os.environ["RWKV_CUDA_ON"] = '0' # '1' to compile CUDA kernel (10x faster), requires c++ compiler & cuda libraries

# For alpha_frequency and alpha_presence, see "Frequency and presence penalties":
# https://platform.openai.com/docs/api-reference/parameter-details


class GenerateResponse(Action):
    
    def __init__(self):
    
        self.model = RWKV(model=current_path+'/RWKV-4-Raven-3B-v9-Eng99%-Other1%-20230411-ctx4096', strategy='cuda fp32i8')
        self.pipeline = PIPELINE(self.model, current_path+'/20B_tokenizer.json') # 20B_tokenizer.json is in https://github.com/BlinkDL/ChatRWKV
        self.args = PIPELINE_ARGS(temperature = 1.0, top_p = 0.7, top_k = 100, # top_k = 0 then ignore
                     alpha_frequency = 0.25,
                     alpha_presence = 0.25,
                     token_ban = [0], # ban the generation of some tokens
                     token_stop = [], # stop generation whenever you see any token here
                     chunk_len = 256) # split input into chunks to save VRAM (shorter -> slower)

        

    
    def name(self) -> Text:
        return "action_raven_generate_text"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user's message from the tracker
        user_message = tracker.latest_message.get('text')
        # Detect the language of the text
        lang = detect(user_message)

        # Create a translator object
        if lang == 'fr':
            translator = Translator(to_lang="en")
            user_message = translator.translate(user_message)
        
        # Generate a response using GPT-4all
        try:
            def my_print(s):
             print(s, end='', flush=True)
             
            generated_text=self.pipeline.generate(user_message, token_count=50, args=self.args, callback=my_print)
            
            # out, state = self.model.forward([187, 510, 1563, 310, 247], None)
            #       # get logits
            # out, state = self.model.forward([187, 510], None)
            # out, state = self.model.forward([1563], state)           # RNN has state (use deepcopy to clone states)
            # out, state = self.model.forward([310, 247], state)
            #generated_text= out.detach().cpu().numpy()                 # same result as above
           

            if lang == 'fr':
                translator = Translator(to_lang="fr")
                generated_text = translator.translate(generated_text)
            
            dispatcher.utter_message(text=generated_text, skip_special_tokens=True)

        except Exception as e:
            logging.exception(f"Error generating response: {e}")

        return []













#################################################################################################################
#RAVEN
import logging,os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from langdetect import detect
from translate import Translator
from multiprocessing import Queue
import re
from pynvml import *
import torch,gc
current_path = os.path.dirname(os.path.abspath(__file__))

# set these before import RWKV
os.environ['RWKV_JIT_ON'] = '1'
os.environ["RWKV_CUDA_ON"] = '1' # '1' to compile CUDA kernel (10x faster), requires c++ compiler & cuda libraries


# Before turning RWKV_CUDA_ON = 1 make sure to install CUDA and do : 
# Linux : 
# export PATH=/usr/local/cuda/bin:$PATH
# export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
# Windows : 
# Install VS2022 build tools (https://aka.ms/vs/17/release/vs_BuildTools.exe select Desktop C++). Reinstall CUDA 11.7 (install VC++ extensions)


from rwkv.model import RWKV
from rwkv.utils import PIPELINE, PIPELINE_ARGS

torch.backends.cudnn.benchmark = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cuda.matmul.allow_tf32 = True
CUDA_LAUNCH_BLOCKING=1

class GenerateResponse(Action):
    
    def __init__(self):
        nvmlInit()
        self.gpu_h = nvmlDeviceGetHandleByIndex(0)
        self.ctx_limit = 1024
        #self.ctx_limit = 512

        # Make sure to convert your model on your strategy with convert.py for fast loading 
        
        #Server
        self.model = RWKV(model=current_path+'/../RWKV/RWKV-4-Raven-7B-v11x-Eng99%-Other1%-20230429-ctx8192Server', strategy='cuda:0 fp16 *16 -> cuda:1 fp16 *16 -> cpu fp32')
        #Local
        #self.model = RWKV(model=current_path+'/RWKV-4-Raven-7B-v10-Eng99%-Other1%-20230418-ctx8192', strategy='cuda fp16 *12 -> cuda fp16i8 *1 -> cpu fp32')

        self.pipeline = PIPELINE(self.model, current_path+'/../RWKV/20B_tokenizer.json')
        
    def generate_prompt(self, instruction, input=None):
        instruction = instruction.strip().replace('\r\n','\n').replace('\n\n','\n')
        input = input.strip().replace('\r\n','\n').replace('\n\n','\n')
        if input:
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a short response that appropriately completes the request.

            # Instruction:
            {instruction}

            # Input:
            {input}

            # Response:
            """
        else:
            return f"""Below is an instruction that describes a task. Write a short response that appropriately completes the request.

            # Instruction:
            {instruction}

            # Response:
            """

    def evaluate(self, instruction, input=None, token_count=200, temperature=1.0, top_p=0.7, presencePenalty=0.1, countPenalty=0.1):
        args = PIPELINE_ARGS(temperature=max(0.2, float(temperature)), top_p=float(top_p),
                             alpha_frequency=countPenalty,
                             alpha_presence=presencePenalty,
                             token_ban=[], # ban the generation of some tokens
                             token_stop=[0]) # stop generation whenever you see any token here

        instruction = instruction.strip().replace('\r\n','\n').replace('\n\n','\n')
        input = input.strip().replace('\r\n','\n').replace('\n\n','\n')
        ctx = self.generate_prompt(instruction, input)

        all_tokens = []
        out_last = 0
        out_str = ''
        occurrence = {}
        state = None
        for i in range(int(token_count)):
            out, state = self.model.forward(self.pipeline.encode(ctx)[-self.ctx_limit:] if i == 0 else [token], state)
            for n in occurrence:
                out[n] -= (args.alpha_presence + occurrence[n] * args.alpha_frequency)

            token = self.pipeline.sample_logits(out, temperature=args.temperature, top_p=args.top_p)
            if token in args.token_stop:
                break
            all_tokens += [token]
            if token not in occurrence:
                occurrence[token] = 1
            else:
                occurrence[token] += 1

            tmp = self.pipeline.decode(all_tokens[out_last:])
            if '\ufffd' not in tmp:
                out_str += tmp
                yield out_str.strip()
                out_last = i + 1

        gpu_info = nvmlDeviceGetMemoryInfo(self.gpu_h)
        print(f'vram {gpu_info.total} used {gpu_info.used} free {gpu_info.free}')

        gc.collect()
        torch.cuda.empty_cache()
        yield out_str.strip()

    
    def name(self) -> Text:
        return "action_raven_generate_text"

    async def run_rwkv_process(self, queue: Queue, user_message, input):
        result = list(self.evaluate(user_message, input, 250, 0.4, 0.7, 0.1, 0.1))
        queue.put(result)
        
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user's message from the tracker
        user_message = tracker.latest_message.get('text')
        if not user_message or not re.search('[a-zA-Z]', user_message):
            return []
        # Detect the language of the text
        lang = detect(user_message)

        # Create a translator object
        if lang == 'fr':
            translator = Translator(to_lang="en")
            user_message = translator.translate(user_message)
        
        # Generate a response using 
        try:
            def my_print(s):
             print(s, end='', flush=True)
             
            input = "Act as a university advisor chatbot from Tunisia and respond only to questions related to Learning and nothing else, make a 20 words reply."
            
            output = self.evaluate(user_message, input, 124, 0.4, 0.7, 0.1, 0.1)

            for value in output:
                print(value)
            generated_text = value
            if lang == 'fr':
                translator = Translator(to_lang="fr")
                generated_text = translator.translate(generated_text)
            
            dispatcher.utter_message(text=generated_text, skip_special_tokens=True)

        except Exception as e:
            logging.exception(f"Error generating response: {e}")

        return []
