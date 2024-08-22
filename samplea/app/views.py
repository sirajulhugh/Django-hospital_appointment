# views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Patient, Doctor, Department, Appointment
from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden
from datetime import datetime
from django.http import Http404
import re
from django.utils.dateparse import parse_date
import random
import string
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.core.files.storage import default_storage
from datetime import date
from django.utils.timezone import now
from django.utils import timezone

# Create your views here.
def register(request):
    return render(request, 'register.html')

def generate_random_digits(length):
    return ''.join(random.choices(string.digits, k=length))

def aboutus(request):
    return render(request, 'aboutus.html')

def contact(request):
    return render(request, 'contact.html')

def register_(request):
    error_message = None

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        age = request.POST.get('age')
        address = request.POST.get('address')
        # pov = request.POST.get('pov')
        date_of_join = request.POST.get('date_of_join')
        phonenumber = request.POST.get('phonenumber')
        images = request.FILES.get('images')
        
        # Validation checks
        if User.objects.filter(email=email).exists():
            error_message = 'Email already exists. Please use a different email.'
        elif len(phonenumber) != 10 :
            error_message = 'Phone number must be 10 digits long.'
        elif user_type not in ['patient', 'doctor']:
            error_message = 'Invalid user type selected.'

        if error_message:
            return render(request, 'register.html', {'error_message': error_message})

        # If no errors, proceed with user creation

        random_number = str(random.randint(100000, 999999))
        username = f'ID {random_number}'
        password = generate_random_digits(6)
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_staff=(user_type == 'doctor')
        )

        if user_type == 'patient':
            Patient.objects.create(
                user=user,
                age=age,
                address=address,
                images=images,
                # pov=pov,
                phonenumber=phonenumber
            )
        elif user_type == 'doctor':
            Doctor.objects.create(
                user=user,
                age=age,
                phonenumber=phonenumber,
                address=address,
                images=images,
                date_of_join=date_of_join
            )

        # Send email with username and password
        send_mail(
            'Your Account Details',
            f'Username(patient ID): {username}\nPassword: {password}',
            'admin@example.com',
            [email],
            fail_silently=False,
        )

        success_message = 'Check your email for username and password.'
        return render(request, 'loginpage.html', {'error_message': success_message})
    
    return render(request, 'register.html')

def loginpage(request):
    return render (request,'loginpage.html')

def home(request):
    return render (request,'home.html')


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('usname')
        password = request.POST.get('passd')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('adminmod')
            elif user.is_staff:
                return redirect('doctormod')
            else:
                return redirect('patientmod')
        else:
            error_message = 'Invalid username or password.'

    return render(request, 'loginpage.html', {'error_message': error_message})

@login_required(login_url='loginpage')
def adminmod(request):
    unassigned_patient_count = Patient.objects.filter(stat=False, user__is_staff=False).count()
    unassigned_doctor_count = Doctor.objects.filter(Q(binary_data=False) | Q(department__isnull=True)).count()
    # unassigned_doctor_count = Doctor.objects.filter(binary_data=False, department__isnull=True).count()
    
    return render(request, 'adminmod.html', {
        'show_patient_notification': unassigned_patient_count > 0,
        'patient_count': unassigned_patient_count,
        'show_doctor_notification': unassigned_doctor_count > 0,
        'doctor_count': unassigned_doctor_count,
    })

# def doctormod(request):
#     doctor = Doctor.objects.filter(user=request.user).first()

#     if doctor and doctor.department is not None and doctor.binary_data:
#         return render(request, 'doctormod.html')
#     else:
#         # If conditions are not met, show authorization message
#         return render(request, 'loginpage.html', {
#             'error_message': "Please wait while your authorization is being processed."
#         })

@login_required(login_url='loginpage')
def patientmod(request):
    # Get the patient associated with the logged-in user
    patient = get_object_or_404(Patient, user=request.user)
    
    # Check if the patient's stat field is True
    if patient.stat:
        # Render the patientmod page if stat is True
        return render(request, 'patientmod.html', {'patient': patient})
    else:
        # Display a message if stat is not True
        message = "Please wait while your authorization is being processed."
        return render(request, 'loginpage.html', {'error_message': message})

def lgout(request):
    auth.logout(request)
    return redirect ('loginpage')

@login_required(login_url='loginpage')
def create_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sub = request.POST.get('sub')
        about = request.FILES.get('about')

        # Create a new Department instance and save it to the database
        department = Department(name=name, sub=sub, about=about)
        department.save()

        return redirect('adminmod')  # Redirect to a success page or another view

    return render(request, 'create_department.html')

@login_required(login_url='loginpage')
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'department_list.html', {'departments': departments})

@login_required(login_url='loginpage')
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'confirm_delete_department.html', {'department': department})

@login_required(login_url='loginpage')
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.name = request.POST.get('name')
        department.sub = request.POST.get('sub')
        department.about = request.FILES.get('about')
        department.save()
        return redirect('department_list')
    return render(request, 'edit_department.html', {'department': department})

@login_required(login_url='loginpage')
def unassigned_patients_view(request):
    department_id = request.GET.get('department')
    
    # Filter doctors where binary_data is not equal to b''
    # doctors = Doctor.objects.exclude(binary_data=b'')
    # departments = Department.objects.all()
    
    # Filter unassigned patients
    unassigned_patients = Patient.objects.filter(stat=False, user__is_staff=False)
    
    # Apply department filter if department_id is provided
    # if department_id:
    #     try:
    #         doctors = doctors.filter(department_id=department_id)
    #     except Department.DoesNotExist:
    #         raise Http404("Department not found")

    return render(request, 'unassigned_patients.html', {
        'unassigned_patients': unassigned_patients,
        # 'departments': departments,
        # 'doctors': doctors,
        # 'selected_department_id': department_id,  # Optional: To keep track of the selected department if needed
    })

@login_required(login_url='loginpage')
def get_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    
    if department_id:
        doctors = Doctor.objects.filter(department_id=department_id)
    else:
        doctors = Doctor.objects.none()
    
    doctor_list = list(doctors.values('id', 'user__first_name'))
    return JsonResponse(doctor_list, safe=False)

@login_required(login_url='loginpage')
# def assign_department_and_doctor(request, patient_id):
#     if request.method == 'POST':
#         # Safely retrieve the department and doctor from POST data
#         department_id = request.POST.get('department')
#         doctor_id = request.POST.get('doctor')

#         if department_id and doctor_id:
#             # Retrieve the patient, department, and doctor
#             patient = get_object_or_404(Patient, id=patient_id)
#             patient.department = Department.objects.get(id=department_id)
#             patient.doctor = Doctor.objects.get(id=doctor_id)
#             patient.save()
#             return redirect('adminmod')
            # department = get_object_or_404(Department, id=department_id)
            # doctor = get_object_or_404(Doctor, id=doctor_id)

            # Assign the department and doctor to the patient
            # patient.department = department
            # patient.doctor = doctor
            # patient.save()


        # else:
            # Handle the case where department or doctor is not provided
            # You might want to redirect or show an error message
            # return redirect('unassigned_patients')  # Example redirection

        # return redirect('adminmod')  # Redirect to the desired view after assignment

    # Handle cases where request method is not POST
    # return redirect('unassigned_patients')

@login_required(login_url='loginpage')
def update_patient_stat(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # Check if the checkbox was checked
        stat = 'stat' in request.POST

        # Update the stat field
        patient.stat = stat
        patient.save()

    return redirect('unassigned_patients')


@login_required(login_url='loginpage')   
def unassigned_doctors_view(request):
    unassigned_doctors = Doctor.objects.filter(Q(binary_data=False) | Q(department__isnull=True))
    departments = Department.objects.all()
    
    return render(request, 'unassigned_doctors.html', {
        'unassigned_doctors': unassigned_doctors,
        'departments': departments,
    })


@login_required(login_url='loginpage')
def assign_doctor_attributes(request, doctor_id):
    if request.method == 'POST':
        department_id = request.POST.get('department')
        binary_data = request.POST.get('binary_data') == 'True'
        
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Only assign department if it was provided in the POST data
        if department_id:
            doctor.department = Department.objects.get(id=department_id)
        
        doctor.binary_data = binary_data
        doctor.save()
        
        return redirect('adminmod')


@login_required(login_url='loginpage')    
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.delete()
    return redirect('unassigned_doctors')

@login_required(login_url='loginpage')
def patient_list_view(request):
    # Filter patients with stat=True
    patients = Patient.objects.filter(stat=True)

    return render(request, 'patient_list.html', {
        'patients': patients
    })

# View patient profile
@login_required(login_url='loginpage')
def view_patient_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'view_patient.html', {'patient': patient})

# Edit patient
@login_required(login_url='loginpage')
def edit_patient_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    departments = Department.objects.all()

    if request.method == 'POST':
        department_id = request.POST.get('department')
        doctor_id = request.POST.get('doctor')

        # Assign new department if provided
        if department_id:
            patient.department = Department.objects.get(id=department_id)
        
        # Assign new doctor if provided
        if doctor_id:
            patient.doctor = Doctor.objects.get(id=doctor_id)

        patient.save()
        return redirect('patient_list')

    return render(request, 'edit_patient.html', {'patient': patient, 'departments': departments})

# Delete patient
@login_required(login_url='loginpage')
def delete_patient_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient.user.delete()  # Assuming a linked user needs to be deleted
    return redirect('patient_list')

@login_required(login_url='loginpage')
def user_list_view(request):
    selected_department_id = request.GET.get('department')
    departments = Department.objects.all()

    if selected_department_id:
        try:
            department = Department.objects.get(id=selected_department_id)
            doctors = Doctor.objects.filter(department=department)
        except Department.DoesNotExist:
            doctors = Doctor.objects.none()
    else:
        doctors = Doctor.objects.none()

    return render(request, 'user_list.html', {
        'departments': departments,
        'doctors': doctors,
        'selected_department_id': selected_department_id,
    })

# View user profile
@login_required(login_url='loginpage')
def view_user_view(request, user_id):
    doctor = get_object_or_404(Doctor, id=user_id)
    return render(request, 'view_user.html', {'doctor': doctor})

# Edit user
@login_required(login_url='loginpage')
def edit_user_view(request, user_id):
    doctor = get_object_or_404(Doctor, id=user_id)
    departments = Department.objects.all()

    if request.method == 'POST':
        department_id = request.POST.get('department')

        # Assign new department if provided
        if department_id:
            doctor.department = Department.objects.get(id=department_id)

        doctor.save()
        return redirect('user_list')  # Redirect to the list view or any other desired view

    return render(request, 'edit_user.html', {'doctor': doctor, 'departments': departments})

# Delete user
@login_required(login_url='loginpage')
def delete_user_view(request, user_id):
    doctor = get_object_or_404(Doctor, id=user_id)
    user = doctor.user  # assuming each doctor has a related user
    user.delete()
    return redirect('user_list')


@login_required(login_url='loginpage')
def view_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'view_user_profile.html', {'user': user})

# View to edit user profile
@login_required(login_url='loginpage')
def edit_user_ad(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = 'is_active' in request.POST
        user.save()
        error_message = "User profile updated successfully."
        return render(request, 'view_user_profile.html', {'error_message': error_message})

    return render(request, 'edit_user_ad.html', {'user': user})


# def view_profile(request):
#     # Get the currently logged-in user
#     user = request.user

#     if request.method == 'POST':
#         # Process the form submission to update the profile
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         username = request.POST.get('username')
#         email = request.POST.get('email')

#         # Update user details
#         user.first_name = first_name
#         user.last_name = last_name
#         user.username = username
#         user.email = email

#         try:
#             user.save()
#             messages.success(request, 'Profile updated successfully!')
#         except Exception as e:
#             messages.error(request, 'Error updating profile: {}'.format(str(e)))

#         return redirect('view_profile')

#     # Render the profile page with user details
#     return render(request, 'view_profile.html', {'user': user})

@login_required(login_url='loginpage')
def doctor_profile(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    return render(request, 'doctor_profile.html', {'doctor': doctor})


@login_required(login_url='loginpage')
def edit_doctor_profile(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    return render(request, 'edit_doctor_profile.html', {'doctor': doctor})


@login_required(login_url='loginpage')
def edit_doctor_profile_submit(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        # Update Doctor information
        doctor.age = request.POST.get('age')
        doctor.phonenumber = request.POST.get('phonenumber')
        doctor.address = request.POST.get('address')
        doctor.date_of_join = request.POST.get('date_of_join')
        
        if 'images' in request.FILES:
            doctor.images = request.FILES['images']
        
        doctor.save()

        # Update User information
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        return redirect('doctor_profile')

    return render(request, 'edit_doctor_profile.html', {'doctor': doctor})

@login_required(login_url='loginpage')
def patient_list_dr(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')
    patients = {appointment.patient for appointment in appointments}  # Get unique patients from the appointments

    return render(request, 'patient_list_dr.html', {'patients': patients})


@login_required(login_url='loginpage')
def patient_profile(request):
    patient = get_object_or_404(Patient, user=request.user)
    return render(request, 'patient_profile.html', {'patient': patient})


@login_required(login_url='loginpage')
def edit_patient_profile(request):
    patient = get_object_or_404(Patient, user=request.user)

    if request.method == 'POST':
        # Get the posted data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        age = request.POST.get('age')
        phonenumber = request.POST.get('phonenumber')
        address = request.POST.get('address')
        images = request.FILES.get('images') if 'images' in request.FILES else patient.images

        # Update Patient data
        patient.age = age
        patient.phonenumber = phonenumber
        patient.address = address
        patient.images = images
        patient.save()

        # Update related User model data
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return redirect('patient_profile')

    return render(request, 'edit_patient_profile.html', {'patient': patient})


 # Check if the patient has already booked an appointment on the selected date
        # existing_appointment = Appointment.objects.filter(patient=patient, date=appointment_date).exists()

        # if existing_appointment:
            # error_message = "You have already booked an appointment on this date."
            # return render(request, 'book_appointment.html', {'error_message': error_message})
            # messages.error(request, "You have already booked an appointment on this date.")
            # return redirect('book_appointment')

@login_required(login_url='loginpage')
def book_appointment(request):
    # Fetch the logged-in patient
    patient = get_object_or_404(Patient, user=request.user)
    # Get all departments for the department dropdown
    departments = Department.objects.all()
    selected_department_id = None
    doctors = []
    selected_doctor = None

    if request.method == 'POST':
        # Handle form submission
        selected_department_id = request.POST.get('department')
        if selected_department_id:
            selected_department = get_object_or_404(Department, id=selected_department_id)
            doctors = Doctor.objects.filter(department=selected_department)

        selected_doctor_id = request.POST.get('doctor')
        if selected_doctor_id:
            selected_doctor = get_object_or_404(Doctor, id=selected_doctor_id, department=selected_department)

        appointment_date = request.POST.get('date')
        description = request.POST.get('description')
        medical_file = request.FILES.get('file')
        selected_slot = request.POST.get('slot')

        # Validate appointment date
        if appointment_date and parse_date(appointment_date) < date.today():
            error_message = "You cannot book an appointment for past dates."
            return render(request, 'book_appointment.html', {
                'departments': departments,
                'doctors': doctors,
                'selected_department_id': selected_department_id,
                'error_message': error_message,
            })

        # Check for slot availability if selected_doctor is set
        if selected_doctor and appointment_date and selected_slot:
            slot_taken = Appointment.objects.filter(
                doctor=selected_doctor, 
                date=appointment_date, 
                **{selected_slot: True}
            ).exists()

            if slot_taken:
                selected_slot_number = selected_slot.split('_')[1]
                error_message = f"Slot {selected_slot_number} is already taken for this doctor on this date."
                return render(request, 'book_appointment.html', {
                    'departments': departments,
                    'doctors': doctors,
                    'selected_department_id': selected_department_id,
                    'error_message': error_message,
                })

            # Create the appointment if slot is available
            Appointment.objects.create(
                date=appointment_date,
                description=description,
                file=medical_file,
                doctor=selected_doctor,
                patient=patient,
                department=selected_department,
                **{selected_slot: True}  
            )

            success_message = "Your appointment has been successfully booked. Wait for the admin approval."
            return render(request, 'patientmod.html', {'success_message': success_message})

    else:
        # Handle initial form load or refresh
        selected_department_id = request.GET.get('department')
        if selected_department_id:
            selected_department = get_object_or_404(Department, id=selected_department_id)
            doctors = Doctor.objects.filter(department=selected_department)

    # Render the form with context
    return render(request, 'book_appointment.html', {
        'departments': departments,
        'doctors': doctors,
        'selected_department_id': selected_department_id,
    })


def get_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    doctors = Doctor.objects.filter(department_id=department_id).select_related('user')
    doctor_data = [
        {'id': doctor.id, 'name': f"{doctor.user.first_name} {doctor.user.last_name}"}
        for doctor in doctors
    ]
    return JsonResponse(doctor_data, safe=False)



# View to list appointments for admin, filtering out approved ones
@login_required(login_url='loginpage')
def appointments_list(request):
    today = now().date()
    
    # Get appointments with Approval=False and dates greater than or equal to today
    appointments = Appointment.objects.filter(Approval=False, date__gte=today)
    
    return render(request, 'appointments_list.html', {'appointments': appointments})

# View to discard an appointment
@login_required(login_url='loginpage')
def discard_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    error_message = "Appointment discarded successfully."
    
    today = now().date()
    # Get appointments with Approval=False and dates greater than or equal to today
    appointments = Appointment.objects.filter(Approval=False, date__gte=today)
    
    return render(request, 'appointments_list.html', {
        'error_message': error_message,
        'appointments': appointments
    })

# View to approve an appointment
@login_required(login_url='loginpage')
def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.Approval = True
    appointment.save()
    error_message = "Appointment approved successfully."
    
    today = now().date()
    # Get appointments with Approval=False and dates greater than or equal to today
    appointments = Appointment.objects.filter(Approval=False, date__gte=today)
    
    return render(request, 'appointments_list.html', {
        'error_message': error_message,
        'appointments': appointments
    })

@login_required(login_url='loginpage')
def doctor_approved_appointments(request):
    # Get the doctor associated with the logged-in user
    doctor = get_object_or_404(Doctor, user=request.user)
    today = now().date()
    
    # Get approved appointments for the logged-in doctor excluding today's and past dates
    appointments = Appointment.objects.filter(doctor=doctor, Approval=True, date__gt=today)
    
    context = {
        'appointments': appointments
    }
    return render(request, 'doctor_approved_appointments.html', context)


@login_required(login_url='loginpage')
def doctormod(request):
    doctor = Doctor.objects.filter(user=request.user).first()

    # Check if the doctor is assigned to a department and is authorized
    if doctor and doctor.department and doctor.binary_data:
        department = doctor.department

        # Fetch today's approved appointments
        today = timezone.now().date()
        todays_appointments = Appointment.objects.filter(
            doctor=doctor,
            date=today,
            Approval=True,
            Status=False
        )
        
        # Count for notifications
        appointment_count = todays_appointments.count()

        # Check if there's any appointment for notifications
        show_doctor_notification = appointment_count > 0

        context = {
            'doctor': doctor,
            'department': department,
            'show_doctor_notification': show_doctor_notification,
            'appointment_count': appointment_count,
        }

        return render(request, 'doctormod.html', context)
    else:
        return render(request, 'loginpage.html', {
            'error_message': "Please wait while your authorization is being processed."
        })

@login_required(login_url='loginpage')
def todays_appointments(request):
    doctor = Doctor.objects.filter(user=request.user).first()

    if doctor:
        # Get today's approved appointments where status is false
        appointments = Appointment.objects.filter(
            doctor=doctor, 
            date=date.today(), 
            Approval=True, 
            Status=False
        )

        return render(request, 'todays_appointments.html', {
            'appointments': appointments
        })
    else:
        messages.error(request, "Unauthorized access.")
        return redirect('doctormod')


@login_required(login_url='loginpage')
def mark_treated(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)

    if appointment:
        appointment.Status = True  # Mark as treated
        appointment.save()
        # messages.success(request, "Appointment marked as treated.")
    
    return redirect('todays_appointments')

@login_required(login_url='loginpage')
def successful_appointments(request):
    doctor = Doctor.objects.filter(user=request.user).first()

    # Ensure the doctor is found
    if doctor:
        # Fetch all successful appointments for the logged-in doctor
        successful_appointments = Appointment.objects.filter(
            doctor=doctor,
            Status=True
        )

        context = {
            'successful_appointments': successful_appointments
        }

        return render(request, 'successful_appointments.html', context)
    else:
        return render(request, 'loginpage.html', {
            'error_message': "You are not authorized to view this page."
        })
    

@login_required(login_url='loginpage')
def patient_upcoming_appointments(request):
    # Get the logged-in patient
    patient = get_object_or_404(Patient, user=request.user)
    
    # Get today's date
    today = now().date()
    
    # Filter appointments: Approved=True, patient matches, and date is today or in the future
    appointments = Appointment.objects.filter(
        patient=patient,
        Approval=True,
        date__gte=today
    )
    
    return render(request, 'patient_upcoming_appointments.html', {'appointments': appointments})


@login_required(login_url='loginpage')
def patient_successful_appointments(request):
    # Get the logged-in patient
    patient = get_object_or_404(Patient, user=request.user)
    
    # Filter successful appointments: Status=True and patient matches
    appointments = Appointment.objects.filter(
        patient=patient,
        Status=True
    )
    
    return render(request, 'patient_successful_appointments.html', {'appointments': appointments})

@login_required(login_url='loginpage')
def reset_password(request):
    return render(request, 'reset_password.html')


@login_required(login_url='loginpage')
def reset_password_(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user

        # Password validation regex: 8 characters, one uppercase, one lowercase, one digit, one special character
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        
        # Check if the current password is correct
        if user.check_password(current_password):
            if new_password == confirm_password:
                if re.match(password_regex, new_password):
                    user.set_password(new_password)
                    user.save()
                    
                    # Update session hash to prevent logout
                    update_session_auth_hash(request, user)
                    
                    
                    error_message = 'Your password has been reset successfully.'
                    return render(request, 'loginpage.html', {'error_message': error_message})
                else:
                    error_message = 'New password does not meet the minimum requirements.'
                    return render(request, 'reset_password.html', {'error_message': error_message})
            else:
                error_message = 'New passwords do not match.'
                return render(request, 'reset_password.html', {'error_message': error_message})
        else:
            error_message = 'Current password is incorrect.'
            return render(request, 'reset_password.html', {'error_message': error_message})
    
    return redirect('loginpage')

@login_required(login_url='loginpage')
def patient_appointments_status(request):
    selected_date = request.GET.get('date')  # Get the date from query parameters

    if selected_date:
        appointments = Appointment.objects.filter(Approval=True, date=selected_date)
    else:
        appointments = Appointment.objects.none()  # Empty queryset if no date is selected

    return render(request, 'patient_appointments_status.html', {'appointments': appointments, 'selected_date': selected_date})


@login_required(login_url='loginpage')
def reset_patient_details(request):
    patient = Patient.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Reset doctor and department to null
        patient.doctor = None
        patient.department = None
        
        # Update purpose of visit (POV) if provided
        pov = request.POST.get('pov')
        if pov:
            patient.pov = pov
        
        patient.save()
        return redirect('patientmod')  # Redirect to the patient's profile or another relevant page
    
    return render(request, 'reset_patient_details.html')