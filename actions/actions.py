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

# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# class ExempleAction(Action):

#     def name(self) -> Text:
#         return "action_exemple"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # récupère la valeur de l'entité "reponse"
#         reponse = tracker.latest_message['entities'][0]['value']

#         if reponse.lower() == "oui":
#             # action à effectuer si la réponse est "oui"
#             dispatcher.utter_message("Très bien! Je vous fournis aini plus d'informations")
#         elif reponse.lower() == "non":
#             # action à effectuer si la réponse est "non"
#             dispatcher.utter_message("Dommage, peut-être une prochaine fois !")
#         else:
#             # action à effectuer si la réponse n'est ni "oui" ni "non"
#             dispatcher.utter_message("Je n'ai pas compris votre réponse, Veuillez répondre par Oui ou par Non.")

#         return []
## action
# actions.py
# from typing import Text, List, Any, Dict
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher

# class ConcatenateAction(Action):
#     def name(self) -> Text:
#         return "action_concatenate_message"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # Obtenir les entités
#         action_name = None
#         message = None

#         for entity in tracker.latest_message["entities"]:
#             if entity["entity"] == "action_name":
#                 action_name = entity["value"]
#             elif entity["entity"] == "message":
#                 message = entity["value"]

#         # Vérifier si les entités ont été trouvées
#         if not action_name:
#             dispatcher.utter_message(text="L'action n'est pas précisée.")
#             return []

#         if not message:
#             dispatcher.utter_message(text="Le message n'est pas précisé.")
#             return []

#         # Concaténer le message à l'action
#         concatenated_message = f"{action_name}: {message}"

#         # Appeler l'action concaténée
#         dispatcher.utter_message(text=concatenated_message)

#         return []
# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher

# class ActionVerifierReponse(Action):

#     def name(self) -> Text:
#         return "action_verifier_reponse"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
#         reponse_utilisateur = tracker.get_slot("reponse_utilisateur")
        
#         if reponse_utilisateur == "oui":
#             print('oui')
#         elif reponse_utilisateur == "non":
#             # La réponse est "non"
#             print('non')
#         else:
#             print('autre chose')
#             # La réponse est autre chose
          
#         return []

# from rasa_sdk import Action
# from rasa_sdk.events import SlotSet

# class ActionDemanderAcceptation(Action):
#     def name(self) -> str:
#         return "demander_acceptation"

#     async def run(self, dispatcher, tracker, domain):
#         # Your custom logic here, e.g. asking a question or sending a message
#         dispatcher.utter_message(text="Voulez-vous continuer?")

#         return []
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionDemanderAcceptation(Action):

    def name(self) -> Text:
        return "demander_acceptation"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # You can add any logic here, for example, sending a message
        dispatcher.utter_message(text="Veuillez accepter pour continuer.")

        return []
