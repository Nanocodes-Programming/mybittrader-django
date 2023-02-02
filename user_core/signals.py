from allauth.account.signals import user_logged_in,user_signed_up
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Site, SendEmail

def send_email(subject,body,recipient):
    site = Site.objects.get(pk=1)
    name = site.name
    address = site.address
    phone_number = site.phone_number
    context ={
        "title": subject,
        "content":body,
        "name": name,
        "address": address,
        "phone_number":phone_number
        }   
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER ,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
 

@receiver(user_logged_in)
def user_logged_in_(request, user, **kwargs):
    subject = 'Login Sucessful,Welcome back to our site'
    body = f"Dear {request.user.username}, We're glad to see you back on our website! We hope you had a great time since your last visit.Don't hesitate to reach out to us if you have any questions or need help with anything. Our customer support team is always here to assist you.Enjoy your time on our site!Best regards,{request.user.username}"
    #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[request.user.email])
    send_email(subject,body,request.user.email)   
        
@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    subject = 'Signup Sucessful,Welcome to our site'
    body_two = f"Dear {user.username},Thank you for signing up for our website! We're excited to have you as a member and look forward to providing you with a great experience.If you have any questions or need help navigating our site, please don't hesitate to reach out to us. Our customer support team is here to assist you.In the meantime, take a look around and see all of the great features and benefits that we have to offer. We're sure you'll find something you love.Best regards,{user.username}"
    body = f"Dear Admin, The new user {user.username} has signed up"
    user_email_model = SendEmail.objects.create(email=user.email,username=user.username)
    user_email_model.save()
    send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[user.email])
    send_email(subject,body_two,user.email)
    send_email(subject,body,settings.RECIPIENT_ADDRESS)