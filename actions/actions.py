# import logging,os
# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from langdetect import detect
# from translate import Translator
# from rwkv.model import RWKV
# from rwkv.utils import PIPELINE, PIPELINE_ARGS
# current_path = os.path.dirname(os.path.abspath(__file__))

# # set these before import RWKV
# os.environ['RWKV_JIT_ON'] = '1'
# os.environ["RWKV_CUDA_ON"] = '0' # '1' to compile CUDA kernel (10x faster), requires c++ compiler & cuda libraries

# # For alpha_frequency and alpha_presence, see "Frequency and presence penalties":
# # https://platform.openai.com/docs/api-reference/parameter-details


# class GenerateResponse(Action):
    
#     def __init__(self):
    
#         self.model = RWKV(model=current_path+'/RWKV-4-Raven-3B-v9-Eng99%-Other1%-20230411-ctx4096', strategy='cuda fp32i8')
#         self.pipeline = PIPELINE(self.model, current_path+'/20B_tokenizer.json') # 20B_tokenizer.json is in https://github.com/BlinkDL/ChatRWKV
#         self.args = PIPELINE_ARGS(temperature = 1.0, top_p = 0.7, top_k = 100, # top_k = 0 then ignore
#                      alpha_frequency = 0.25,
#                      alpha_presence = 0.25,
#                      token_ban = [0], # ban the generation of some tokens
#                      token_stop = [], # stop generation whenever you see any token here
#                      chunk_len = 256) # split input into chunks to save VRAM (shorter -> slower)

        

    
#     def name(self) -> Text:
#         return "action_raven_generate_text"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Get the user's message from the tracker
#         user_message = tracker.latest_message.get('text')
#         # Detect the language of the text
#         lang = detect(user_message)

#         # Create a translator object
#         if lang == 'fr':
#             translator = Translator(to_lang="en")
#             user_message = translator.translate(user_message)
        
#         # Generate a response using GPT-4all
#         try:
#             def my_print(s):
#              print(s, end='', flush=True)
             
#             generated_text=self.pipeline.generate(user_message, token_count=50, args=self.args, callback=my_print)
            
#             # out, state = self.model.forward([187, 510, 1563, 310, 247], None)
#             #       # get logits
#             # out, state = self.model.forward([187, 510], None)
#             # out, state = self.model.forward([1563], state)           # RNN has state (use deepcopy to clone states)
#             # out, state = self.model.forward([310, 247], state)
#             #generated_text= out.detach().cpu().numpy()                 # same result as above
           

#             if lang == 'fr':
#                 translator = Translator(to_lang="fr")
#                 generated_text = translator.translate(generated_text)
            
#             dispatcher.utter_message(text=generated_text, skip_special_tokens=True)

#         except Exception as e:
#             logging.exception(f"Error generating response: {e}")

#         return []
