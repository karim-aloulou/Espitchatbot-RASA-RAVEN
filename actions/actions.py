import random
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from fuzzywuzzy import process

# Dictionnaires globaux des sujets
topics = {
    "prix_fr": {"modalite_fr","rentree_fr","concours_admission_fr"},
    "dejainscrit_fr": {"place_fr","B2_fr","reclamation_confirmation_admission_fr"},
    "autre_fr": {"procedure_inscription_fr","cout_formation_fr","date_preinscription_fr","reporter_entretien_fr","mobilite_internationale_fr", "avantage_alternance_fr","modalites_paiement_fr"},
    "cour_fr": {"courssoir_fr", "difference_3A_3B_fr"},
    "autre_ang":{"procedure_inscription_ang","rentree_ang","cout_formation_ang","cout_formation_fr",}
    
}
class ActionRandomTopic(Action):
    def name(self) -> Text:
        return "action_random_topic"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        global topics

        # Récupère l'intention précédente
        previous_intent = tracker.latest_message["intent"].get("name")

        # Trouve le dictionnaire approprié et supprime l'intention précédente
        selected_dict = None
        for topic_key, topic_dict in topics.items():
            if previous_intent in topic_dict:
                topic_dict.remove(previous_intent)
                selected_dict = topic_dict
                break
        
        random_topic = None  # Initialisation de random_topic

        if selected_dict is not None and len(selected_dict) > 0:
            # Sélectionne un sujet aléatoire parmi les sujets restants
            random_topic = None
            random_topic = random.choice(list(selected_dict))

            # Supprime le suffixe "_fr" ou "_ang" du mot
            if "_ang" in random_topic:
                topic_without_suffix = random_topic.replace("_ang", "")
                dispatcher.utter_message(text=f"Do you want to know more about {topic_without_suffix}?")
            else:
                topic_without_suffix = random_topic.replace("_fr", "")
                dispatcher.utter_message(text=f"Voulez-vous en savoir plus sur {topic_without_suffix}?")

            return [SlotSet("topic", random_topic)]
        else:
            print(previous_intent)
            print(random_topic)
            if random_topic is None and "_ang" in previous_intent:
                dispatcher.utter_message(text="I'm here for more information.")
            else:
                dispatcher.utter_message(text="Je reste à votre disposition.")
                
            return [SlotSet("topic", None)]


class ActionTopicInfo(Action):
    def name(self) -> Text:
        return "action_topic_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        topic = tracker.get_slot("topic")

        # Vérifie si l'utterance 'utter_topic' est définie dans le domaine
        if f"utter_{topic}" in domain["responses"]:
            dispatcher.utter_message(template=f"utter_{topic}")
        else:
            dispatcher.utter_message(text="Désolé, je n'ai pas d'informations sur ce sujet.")

        return []
    

cours_info_fr = {
    "cours du jour (tunisien)": "Pour effectuer votre inscription à ESPRIT Ingénieur, il y a lieu de compléter les informations requises dans le formulaire ci-après. \n Vous devez notamment choisir la spécialité et le niveau d'admission en fonction de votre spécialité  d’origine et de votre niveau d’études. \n https://esprit-tn.com/admission/Admission_CJ.aspx",
    "cours du jour (internationaux)": "Pour effectuer votre inscription à ESPRIT Ingénieur, il y a lieu de compléter les informations requises dans le formulaire ci-après. \n Vous devez notamment choisir la spécialité et le niveau d'admission en fonction de votre spécialité  d’origine et de votre niveau d’études. \n https://esprit-tn.com/admission/ETR.aspx",
    "cours du soir (tunisien)": "Pour effectuer votre inscription à ESPRIT Ingénieur, il y a lieu de compléter les informations requises dans le formulaire ci-après. \n Vous devez notamment choisir la spécialité et le niveau d'admission en fonction de votre spécialité  d’origine et de votre niveau d’études. \n https://esprit-tn.com/admission/CS.aspx"
}


class ActionCours(Action):
    def name(self) -> Text:
        return "action_cours_fr"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        cours = tracker.get_slot("cours_fr")
        
        # Use fuzzy string matching to find the closest matching key
        best_match = process.extractOne(cours, cours_info_fr.keys())
        
        if best_match:
            matched_key, confidence = best_match
            if confidence >= 80:  # Set a confidence threshold (e.g., 80%)
                nature_cours = cours_info_fr.get(matched_key)
                output = "L'inscription au {} : \n {}".format(matched_key, nature_cours)
            else:
                output = "Désolé, je ne reconnais pas ce cours : {}".format(cours)
        else:
            output = "Désolé, je ne reconnais pas ce cours : {}".format(cours)

        dispatcher.utter_message(text=output)
        return []


cours_info_ang = {
    "day course (Tunisian)": "To register for ESPRIT Engineering, please complete the required information in the form below. \n You must choose the specialty and admission level according to your original specialty and level of study. \n https://esprit-tn.com/admission/Admission_CJ.aspx",
    "day course (International)": "To register for ESPRIT Engineering, please complete the required information in the form below. \n You must choose the specialty and admission level according to your original specialty and level of study. \n https://esprit-tn.com/admission/ETR.aspx",
    "evening course (Tunisian)": "To register for ESPRIT Engineering, please complete the required information in the form below. \n You must choose the specialty and admission level according to your original specialty and level of study. \n https://esprit-tn.com/admission/CS.aspx"
}

class ActionCoursAng(Action):
    def name(self) -> Text:
        return "action_cours_ang"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        cours = tracker.get_slot("cours_ang")
        
        # Use fuzzy string matching to find the closest matching key
        best_match = process.extractOne(cours, cours_info_ang.keys())
        
        if best_match:
            matched_key, confidence = best_match
            if confidence >= 80:  # Set a confidence threshold (e.g., 80%)
                nature_cours = cours_info_ang.get(matched_key)
                output = "Registration for the {} : \n {}".format(matched_key, nature_cours)
            else:
                output = "Sorry, I do not recognize this course: {}".format(cours)
        else:
            output = "Sorry, I do not recognize this course: {}".format(cours)

        dispatcher.utter_message(text=output)
        return []



cout_fr = {
    "un étudiant tunisien (cours du jour)": "7350 DT",
    "un étudiant non pris en charge par une entreprise": "6200 DT",
    "un étudiant tunisien (cours du soir)": "7200 DT",
    "un étudiant international": "3000 €"
}



class ActionCoutFormation(Action):
    def name(self) -> Text:
        return "action_cout_fr"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        student_type = tracker.get_slot("type_cout_fr")

        # Use fuzzy string matching to find the closest matching key
        best_match = process.extractOne(student_type, cout_fr.keys())

        if best_match:
            matched_key, confidence = best_match
            if confidence >= 80:  # Set a confidence threshold (e.g., 80%)
                cout_formation = cout_fr.get(matched_key)
                output = "Le coût total de la formation pour {} est : {}".format(matched_key, cout_formation)
            else:
                output = "Désolé, je ne reconnais pas ce type d'étudiant : {}".format(student_type)
        else:
            output = "Désolé, je ne reconnais pas ce type d'étudiant : {}".format(student_type)

        dispatcher.utter_message(text=output)
        return []



cost_en = {
    "a Tunisian student (day courses)": "7350 DT",
    "a student not sponsored by a company": "6200 DT",
    "a Tunisian student (evening courses)": "7200 DT",
    "an international student": "3000 €"
}


class ActionCostOfEducation(Action):
    def name(self) -> Text:
        return "action_cout_ang"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        student_type = tracker.get_slot("type_cout_ang")

        # Use fuzzy string matching to find the closest matching key
        best_match = process.extractOne(student_type, cost_en.keys())

        if best_match:
            matched_key, confidence = best_match
            if confidence >= 80:  # Set a confidence threshold (e.g., 80%)
                cost_of_education = cost_en.get(matched_key)
                output = "The total cost of education for {} is: {}".format(matched_key, cost_of_education)
            else:
                output = "Sorry, I don't recognize this type of student: {}".format(student_type)
        else:
            output = "Sorry, I don't recognize this type of student: {}".format(student_type)

        dispatcher.utter_message(text=output)
        return []

rentree_ang = {
    "1st year": "APP0 activity will be held during the week of September 6",
    "2nd year": "the resumption of classes for former students will take place from September 13",
    "3rd year": "the resumption of classes for former students will take place from September 13",
    "4th year": "the resumption of classes for former students will take place from September 13",
    "5th year": "the resumption of classes for former students will take place from September 13"
}


class ActionRentreeAng(Action):
    def name(self) -> Text:
        return "action_rentree_ang"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot("rentree_niveau_ang")

        # Use fuzzy string matching to find the closest matching key
        best_match = process.extractOne(year, rentree_ang.keys())

        if best_match:
            matched_key, confidence = best_match
            if confidence >= 80:  # Set a confidence threshold (e.g., 80%)
                rentree_info = rentree_ang.get(matched_key)
                output = "For {}: {}\nFor more information: https://prit.tn/admission/esprit-ingenieur".format(matched_key, rentree_info)
            else:
                output = "Sorry, I do not recognize this year : {}".format(year)
        else:
            output = "Sorry, I do not recognize this year : {}".format(year)

        dispatcher.utter_message(text=output)
        return []


rentree_fr = {
    "1 ère année": "L'activité APP0 se déroulera pendant la semaine du 6 septembre",
    "2 ème année": "La reprise des cours pour les anciens étudiants aura lieu à partir du 13 septembre",
    "3 ème année": "La reprise des cours pour les anciens étudiants aura lieu à partir du 13 septembre",
    "4 ème année": "La reprise des cours pour les anciens étudiants aura lieu à partir du 13 septembre",
    "5 ème année": "La reprise des cours pour les anciens étudiants aura lieu à partir du 13 septembre"
}



class ActionRentreeFr(Action):
    def name(self) -> Text:
        return "action_rentree_fr"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot("rentree_niveau_fr")

        # Use fuzzy string matching to find the closest matching key
        best_match = process.extractOne(year, rentree_fr.keys())

        if best_match:
            matched_key, confidence = best_match
            if confidence >= 80:  # Set a confidence threshold (e.g., 80%)
                rentree_info = rentree_fr.get(matched_key)
                output = "Pour {}: {}\nPour plus d'informations: https://prit.tn/admission/esprit-ingenieur".format(matched_key, rentree_info)
            else:
                output = "Désolé, je ne reconnais pas cette année : {}".format(year)
        else:
            output = "Désolé, je ne reconnais pas cette année : {}".format(year)

        dispatcher.utter_message(text=output)
        return []
    















# # import logging,os
# # from typing import Any, Text, Dict, List
# # from rasa_sdk import Action, Tracker
# # from rasa_sdk.executor import CollectingDispatcher
# # from langdetect import detect
# # from translate import Translator
# # from rwkv.model import RWKV
# # from rwkv.utils import PIPELINE, PIPELINE_ARGS
# # current_path = os.path.dirname(os.path.abspath(__file__))

# # # set these before import RWKV
# # os.environ['RWKV_JIT_ON'] = '1'
# # os.environ["RWKV_CUDA_ON"] = '0' # '1' to compile CUDA kernel (10x faster), requires c++ compiler & cuda libraries

# # # For alpha_frequency and alpha_presence, see "Frequency and presence penalties":
# # # https://platform.openai.com/docs/api-reference/parameter-details


# # class GenerateResponse(Action):
    
# #     def __init__(self):
    
# #         self.model = RWKV(model=current_path+'/RWKV-4-Raven-3B-v9-Eng99%-Other1%-20230411-ctx4096', strategy='cuda fp32i8')
# #         self.pipeline = PIPELINE(self.model, current_path+'/20B_tokenizer.json') # 20B_tokenizer.json is in https://github.com/BlinkDL/ChatRWKV
# #         self.args = PIPELINE_ARGS(temperature = 1.0, top_p = 0.7, top_k = 100, # top_k = 0 then ignore
# #                      alpha_frequency = 0.25,
# #                      alpha_presence = 0.25,
# #                      token_ban = [0], # ban the generation of some tokens
# #                      token_stop = [], # stop generation whenever you see any token here
# #                      chunk_len = 256) # split input into chunks to save VRAM (shorter -> slower)

        

    
# #     def name(self) -> Text:
# #         return "action_raven_generate_text"

# #     def run(self, dispatcher: CollectingDispatcher,
# #             tracker: Tracker,
# #             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

# #         # Get the user's message from the tracker
# #         user_message = tracker.latest_message.get('text')
# #         # Detect the language of the text
# #         lang = detect(user_message)

# #         # Create a translator object
# #         if lang == 'fr':
# #             translator = Translator(to_lang="en")
# #             user_message = translator.translate(user_message)
        
# #         # Generate a response using GPT-4all
# #         try:
# #             def my_print(s):
# #              print(s, end='', flush=True)
             
# #             generated_text=self.pipeline.generate(user_message, token_count=50, args=self.args, callback=my_print)
            
# #             # out, state = self.model.forward([187, 510, 1563, 310, 247], None)
# #             #       # get logits
# #             # out, state = self.model.forward([187, 510], None)
# #             # out, state = self.model.forward([1563], state)           # RNN has state (use deepcopy to clone states)
# #             # out, state = self.model.forward([310, 247], state)
# #             #generated_text= out.detach().cpu().numpy()                 # same result as above
           

# #             if lang == 'fr':
# #                 translator = Translator(to_lang="fr")
# #                 generated_text = translator.translate(generated_text)
            
# #             dispatcher.utter_message(text=generated_text, skip_special_tokens=True)

# #         except Exception as e:
# #             logging.exception(f"Error generating response: {e}")

# #         return []

# # from typing import Any, Text, Dict, List
# # from rasa_sdk import Action, Tracker
# # from rasa_sdk.executor import CollectingDispatcher
# # from rasa_sdk.events import SlotSet

# # class ExempleAction(Action):

# #     def name(self) -> Text:
# #         return "action_exemple"

# #     def run(self, dispatcher: CollectingDispatcher,
# #             tracker: Tracker,
# #             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

# #         # récupère la valeur de l'entité "reponse"
# #         reponse = tracker.latest_message['entities'][0]['value']

# #         if reponse.lower() == "oui":
# #             # action à effectuer si la réponse est "oui"
# #             dispatcher.utter_message("Très bien! Je vous fournis aini plus d'informations")
# #         elif reponse.lower() == "non":
# #             # action à effectuer si la réponse est "non"
# #             dispatcher.utter_message("Dommage, peut-être une prochaine fois !")
# #         else:
# #             # action à effectuer si la réponse n'est ni "oui" ni "non"
# #             dispatcher.utter_message("Je n'ai pas compris votre réponse, Veuillez répondre par Oui ou par Non.")

# #         return []
# ## action
# # actions.py
# # from typing import Text, List, Any, Dict
# # from rasa_sdk import Action, Tracker
# # from rasa_sdk.executor import CollectingDispatcher

# # class ConcatenateAction(Action):
# #     def name(self) -> Text:
# #         return "action_concatenate_message"

# #     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

# #         # Obtenir les entités
# #         action_name = None
# #         message = None

# #         for entity in tracker.latest_message["entities"]:
# #             if entity["entity"] == "action_name":
# #                 action_name = entity["value"]
# #             elif entity["entity"] == "message":
# #                 message = entity["value"]

# #         # Vérifier si les entités ont été trouvées
# #         if not action_name:
# #             dispatcher.utter_message(text="L'action n'est pas précisée.")
# #             return []

# #         if not message:
# #             dispatcher.utter_message(text="Le message n'est pas précisé.")
# #             return []

# #         # Concaténer le message à l'action
# #         concatenated_message = f"{action_name}: {message}"

# #         # Appeler l'action concaténée
# #         dispatcher.utter_message(text=concatenated_message)

# #         return []
# # from typing import Any, Text, Dict, List
# # from rasa_sdk import Action, Tracker
# # from rasa_sdk.executor import CollectingDispatcher

# # class ActionVerifierReponse(Action):

# #     def name(self) -> Text:
# #         return "action_verifier_reponse"

# #     def run(self, dispatcher: CollectingDispatcher,
# #             tracker: Tracker,
# #             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
# #         reponse_utilisateur = tracker.get_slot("reponse_utilisateur")
        
# #         if reponse_utilisateur == "oui":
# #             print('oui')
# #         elif reponse_utilisateur == "non":
# #             # La réponse est "non"
# #             print('non')
# #         else:
# #             print('autre chose')
# #             # La réponse est autre chose
          
# #         return []

# # from rasa_sdk import Action
# # from rasa_sdk.events import SlotSet

# # class ActionDemanderAcceptation(Action):
# #     def name(self) -> str:
# #         return "demander_acceptation"

# #     async def run(self, dispatcher, tracker, domain):
# #         # Your custom logic here, e.g. asking a question or sending a message
# #         dispatcher.utter_message(text="Voulez-vous continuer?")

# #         return []
# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# class ActionSetModePro(Action):

#     def name(self) -> Text:
#         return "action_set_mode_pro"

#     async def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:

#         intent = tracker.latest_message['intent'].get('name')

#         if intent == 'pro_mode':
#             return [SlotSet("mode_pro", True)]
#         else:
#             return [SlotSet("mode_pro", False)]


# class ActionDemanderAcceptation(Action):

#     def name(self) -> Text:
#         return "demander_acceptation"

#     async def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:

#         # You can add any logic here, for example, sending a message
#         dispatcher.utter_message(text="Veuillez accepter pour continuer.")

#         return []

# class ActionChooseMode(Action):
#     def name(self):
#         return "action_choose_mode"
    
#     def run(self, dispatcher, tracker, domain):
#         mode = tracker.latest_message.get('text').lower()
#         if mode == "normal":
#             dispatcher.utter_message("Vous êtes maintenant en mode normal.")
#             return [ SlotSet("mode_pro", False)]
#         elif mode == "pro":
#             dispatcher.utter_message("Vous êtes maintenant en mode pro.")
#             return [ SlotSet("mode_pro", True)]
#         else:
#             dispatcher.utter_message(template="utter_wrong_mode")
#             return []

# class ActionGreetAndAskMode(Action):
#     def name(self):
#         return "action_greet_and_ask_mode"

#     def run(self, dispatcher, tracker, domain):
#         dispatcher.utter_message(text="Salut ! Comment ça va ?")
#         dispatcher.utter_message(text="Veuillez choisir le mode de conversation: normal ou pro.")
#         return []