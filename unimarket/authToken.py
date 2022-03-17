import six 
from django.contrib.auth.tokens import PasswordResetTokenGenerator 

class MemberActivationTokenGenerator(PasswordResetTokenGenerator): 
    def _make_hash_value(self, dto, timestamp): 
        return (six.text_type(dto.pk) + six.text_type(timestamp)) + six.text_type(dto.is_active) 
        
member_activation_token = MemberActivationTokenGenerator()
