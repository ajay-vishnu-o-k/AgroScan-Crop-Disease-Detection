# =========================================================
# AgroScan Context Memory (UPDATED)
# =========================================================

class ChatbotMemory:

    def __init__(self):

        self.memory = {

            "last_crop": None,
            "last_disease": None,
            "last_intent": None,

            "last_sub_intent": None,   # ✅ NEW ADDITION

            "awaiting_crop_confirmation": False,
            "possible_crops": [],
            "conversation_history": [],

            "cultivation_mode": False
        }

    # =====================================================
    # Crop
    # =====================================================
    def set_crop(self, crop):
        self.memory["last_crop"] = crop

    def get_crop(self):
        return self.memory["last_crop"]

    # =====================================================
    # Disease
    # =====================================================
    def set_disease(self, disease):
        self.memory["last_disease"] = disease

    def get_disease(self):
        return self.memory["last_disease"]

    # =====================================================
    # Intent
    # =====================================================
    def set_intent(self, intent):
        self.memory["last_intent"] = intent

    def get_intent(self):
        return self.memory["last_intent"]

    # =====================================================
    # 🔥 NEW: Sub Intent (soil/sowing/etc.)
    # =====================================================
    def set_sub_intent(self, sub_intent):
        self.memory["last_sub_intent"] = sub_intent

    def get_sub_intent(self):
        return self.memory["last_sub_intent"]

    # =====================================================
    # Confirmation Handling
    # =====================================================
    def set_confirmation(self, state, possible_crops=None):

        self.memory["awaiting_crop_confirmation"] = state

        if possible_crops:
            self.memory["possible_crops"] = possible_crops

    def needs_confirmation(self):
        return self.memory["awaiting_crop_confirmation"]

    def get_possible_crops(self):
        return self.memory["possible_crops"]

    # =====================================================
    # History
    # =====================================================
    def add_to_history(self, user_message, bot_response):

        self.memory["conversation_history"].append({
            "user": user_message,
            "bot": bot_response
        })

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

            "last_sub_intent": None,   # ✅ RESET INCLUDED

            "awaiting_crop_confirmation": False,
            "possible_crops": [],
            "conversation_history": [],

            "cultivation_mode": False
        }

    # =====================================================
    # Cultivation Mode
    # =====================================================
    def set_cultivation_mode(self, state):
        self.memory["cultivation_mode"] = state

    def get_cultivation_mode(self):
        return self.memory.get("cultivation_mode", False)


# Global Memory Object
chat_memory = ChatbotMemory()