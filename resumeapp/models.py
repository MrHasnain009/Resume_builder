# resume_builder/models.py
from django.db import models
from django.contrib.auth.models import User # اگر آپ Django کے بلٹ ان User ماڈل سے لنک کرنا چاہتے ہیں

# UserProfile ماڈل میں ذاتی معلومات اور پروفائل پکچر شامل ہے۔
class UserProfile(models.Model):
    # یہ User ماڈل سے ون-ٹو-ون لنک ہے، ہر صارف کے لیے ایک پروفائل
    # اگر آپ لاگ ان سسٹم استعمال نہیں کر رہے تو آپ اسے ہٹا سکتے ہیں
    # اور صرف ایک UserProfile بنا سکتے ہیں یا اسے کسی اور طریقے سے ہینڈل کر سکتے ہیں۔
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)

    # ImageField تصویر کو MEDIA_ROOT کے اندر 'profile_pics/' میں سٹور کرے گا
    # blank=True اور null=True کا مطلب ہے کہ یہ فیلڈ خالی ہو سکتی ہے۔
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        # اگر پورا نام موجود ہے تو اسے دکھائیں، ورنہ یوزر نیم
        return self.full_name or (self.user.username if self.user else f"Profile {self.id}")

# تعلیم کی تفصیلات کے لیے ماڈل
class Education(models.Model):
    # یہ UserProfile سے فارن کی (foreign key) کے ذریعے منسلک ہے
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=255)
    university = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50) # تاریخوں کو سٹرنگ کے طور پر سٹور کر رہے ہیں
    end_date = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.degree} from {self.university}"

# تجربے کی تفصیلات کے لیے ماڈل
class Experience(models.Model):
    # یہ UserProfile سے فارن کی (foreign key) کے ذریعے منسلک ہے
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experience')
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50) # تاریخوں کو سٹرنگ کے طور پر سٹور کر رہے ہیں
    end_date = models.CharField(max_length=50, blank=True)
    responsibilities = models.TextField() # ذمہ داریاں ایک بڑے ٹیکسٹ بلاک کے طور پر

    def __str__(self):
        return f"{self.job_title} at {self.company}"

# مہارتوں کی تفصیلات کے لیے ماڈل
class Skill(models.Model):
    # یہ UserProfile سے فارن کی (foreign key) کے ذریعے منسلک ہے
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Create your models here.