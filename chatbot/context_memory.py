# =========================================================
# AgroScan Context Memory
# =========================================================

class ChatbotMemory:

    def __init__(self):

        self.memory = {

            "last_crop": None,

            "last_disease": None,

            "last_intent": None,

            "awaiting_crop_confirmation": False,

            "possible_crops": [],

            "conversation_history": []
        }

    # =====================================================
    # Save Crop
    # =====================================================

    def set_crop(self, crop):

        self.memory["last_crop"] = crop

    # =====================================================
    # Save Disease
    # =====================================================

    def set_disease(self, disease):

        self.memory["last_disease"] = disease

    # =====================================================
    # Save Intent
    # =====================================================

    def set_intent(self, intent):

        self.memory["last_intent"] = intent

    # =====================================================
    # Get Crop
    # =====================================================

    def get_crop(self):

        return self.memory["last_crop"]

    # =====================================================
    # Get Disease
    # =====================================================

    def get_disease(self):

        return self.memory["last_disease"]

    # =====================================================
    # Get Intent
    # =====================================================

    def get_intent(self):

        return self.memory["last_intent"]

    # =====================================================
    # Store Confirmation State
    # =====================================================

    def set_confirmation(self, state, possible_crops=None):

        self.memory["awaiting_crop_confirmation"] = state

        if possible_crops:

            self.memory["possible_crops"] = possible_crops

    # =====================================================
    # Get Confirmation State
    # =====================================================

    def needs_confirmation(self):

        return self.memory["awaiting_crop_confirmation"]

    # =====================================================
    # Get Possible Crops
    # =====================================================

    def get_possible_crops(self):

        return self.memory["possible_crops"]

    # =====================================================
    # Save Conversation
    # =====================================================

    def add_to_history(self, user_message, bot_response):

        self.memory["conversation_history"].append({

            "user": user_message,

            "bot": bot_response
        })

    # =====================================================
    # Get History
    # =====================================================

    def get_history(self):

        return self.memory["conversation_history"]

    # =====================================================
    # Clear Memory
    # =====================================================

    def clear_memory(self):

        self.memory = {

            "last_crop": None,

            "last_disease": None,

            "last_intent": None,

            "awaiting_crop_confirmation": False,

            "possible_crops": [],

            "conversation_history": []
        }


# =========================================================
# Global Memory Object
# =========================================================

chat_memory = ChatbotMemory()
