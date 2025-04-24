from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage



def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']    
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password'] 
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()   

            current_site = get_current_site(request)
            mail_subject = "Activa tu cuenta en Ecommerce"
            body = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'dominio': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()

            # messages.success(request, 'Registro Exitoso')
            return redirect('/accounts/login/?command=verification&email='+email)

    context = {
        'form': form
    }

    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':    # Validamos el metodo, verificamos si es de tipo post
        email = request.POST['email']
        password = request.POST['password']

        # Proceso de autenticaciòn
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Inicio de Sesiòn')
            return redirect('dashboard')
        else:
            messages.error(request, 'Las credenciales son incorrectas')
            return redirect('login')

    return render(request, 'accounts/login.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has cerrado sesiòn')

    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades, tu cuenta esta activa!')
        return redirect('login')
    else:
        messages.error(request, 'La activaciòn es invalida')
        return redirect('register')
    

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')



def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        
        # Evaluamos si el email existe en la base de datos
        if Account.objects.filter(email=email).exists():     # Es True or False?
            user = Account.objects.get(email__exact=email)      # Si el usuario existe, lo almacenamos en user    email__exact=email --> email de la base de datos es exactamente el mismo del email que estamos obteniendo del request?

            current_site = get_current_site(request)    # Pagina actual
            mail_subject = 'Resetear Password'
            body = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'dominio': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()

            messages.success(request, 'Un email fue enviado a tu bandeja de entrada para resetear tu password, recuerda revisar el spam')
            return redirect('login')
        else:
            messages.error(request, 'La cuenta de usuario no existe')
            return redirect('forgotPassord')

    return render(request, 'accounts/forgotPassword.html')



def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor resetea tu password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'El link ha expirado')
        return redirect('login')
    

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)    # seteamos el nuevo password
            user.save()
            messages.success(request, 'El password se reseteo correctamente')
            return redirect('login')
        
        else:
            messages.error(request, 'El password de confirmaciòn no coincide')
            return redirect('resetPassword')
        
    else:
        return render(request, 'accounts/resetPassword.html')