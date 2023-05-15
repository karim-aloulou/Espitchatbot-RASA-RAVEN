import random
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from fuzzywuzzy import process

# Dictionnaires globaux des sujets
topics = {
    "noninscrit_fr": {"inscri_bac_fr","inscri_ing_info_fr","double_diplome_fr","certificat_fr","info_generale_esprit_fr","avantage_esprit_fr","difference_3A_3B_fr","regime_etude_fr","filiere_fr","applicabilite_formation_fr","reconnaissance_diplome_fr","partenaires_fr","rentree_fr","courssoir_fr"},
    "dejainscrit_fr": {"club_fr","note_fr","modalite_fr","conseil_classe_fr","mobilite_internationale_fr","valider_module_fr","admis_fr","date_res_fr","classe_fr","obtention_diplome_fr","absence_examen_fr","reduction_premier_fr","B2_fr"},
    "stage_fr": {"stage_fr","procedure_stage_fr","avantage_alternance_fr"},
    "redouble_fr": {"credit_fr","double_correction_fr","redoublement_fr","ratt_fr"},
    "prix_fr":{"cout_restauration_fr","cout_hebergement_fr","carte_amen_fr","paiement_par_tranche_fr","cout_formation_fr","modalites_paiement_fr"},
    "admission_fr":{"date_preinscription_fr","concours_admission_fr","procedure_inscription_fr","annulation_inscription_fr","reporter_entretien_fr"},
    
    "noninscrit_ang": {"inscri_bac_ang","inscri_ing_info_ang","double_diplome_ang","certificat_ang","info_generale_esprit_ang","avantage_esprit_ang","difference_3A_3B_ang","regime_etude_ang","filiere_ang","applicabilite_formation_ang","reconnaissance_diplome_ang","partenaires_ang","rentree_ang","courssoir_ang"},
    "dejainscrit_ang": {"club_ang","note_ang","modalite_ang","conseil_classe_ang","mobilite_internationale_ang","valider_module_ang","admis_ang","date_res_ang","classe_ang","obtention_diplome_ang","absence_examen_ang","reduction_premier_ang","B2_ang"},
    "stage_ang": {"stage_ang","procedure_stage_ang","avantage_alternance_ang"},
    "redouble_ang": {"credit_ang","double_correction_ang","redoublement_ang","ratt_ang"},
    "prix_ang":{"cout_restauration_ang","cout_hebergement_ang","carte_amen_ang","paiement_par_tranche_ang","cout_formation_ang","modalites_paiement_ang"},
    "admission_ang":{"date_preinscription_ang","concours_admission_ang","procedure_inscription_ang","annulation_inscription_ang","reporter_entretien_ang"}
     
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
            if confidence >= 40:  # Set a confidence threshold (e.g., 80%)
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
            if confidence >= 40:  # Set a confidence threshold (e.g., 80%)
                nature_cours = cours_info_ang.get(matched_key)
                output = "Registration for the {} : \n {}".format(matched_key, nature_cours)
            else:
                output = "Sorry, I do not recognize this course: {}".format(cours)
        else:
            output = "Sorry, I do not recognize this course: {}".format(cours)

        dispatcher.utter_message(text=output)
        return []



cout_fr = {
    "un étudiant tunisien (cours du jour)": "8100 DT",
    "un étudiant non pris en charge par une entreprise": "6200 DT",
    "un étudiant tunisien (cours du soir)": "6500 DT",
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
            if confidence >= 40:  # Set a confidence threshold (e.g., 80%)
                cout_formation = cout_fr.get(matched_key)
                output = "Le coût total de la formation pour {} est : {}".format(matched_key, cout_formation)
            else:
                output = "Désolé, je ne reconnais pas ce type d'étudiant : {}".format(student_type)
        else:
            output = "Désolé, je ne reconnais pas ce type d'étudiant : {}".format(student_type)

        dispatcher.utter_message(text=output)
        return []



cost_en = {
    "a Tunisian student (day courses)": "8100 DT",
    "a student not sponsored by a company": "6200 DT",
    "a Tunisian student (evening courses)": "6500 DT",
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
            if confidence >= 40:  # Set a confidence threshold (e.g., 80%)
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
            if confidence >= 40:  # Set a confidence threshold (e.g., 80%)
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
            if confidence >= 40:  # Set a confidence threshold (e.g., 80%)
                rentree_info = rentree_fr.get(matched_key)
                output = "Pour {}: {}\nPour plus d'informations: https://prit.tn/admission/esprit-ingenieur".format(matched_key, rentree_info)
            else:
                output = "Désolé, je ne reconnais pas cette année : {}".format(year)
        else:
            output = "Désolé, je ne reconnais pas cette année : {}".format(year)

        dispatcher.utter_message(text=output)
        return []
