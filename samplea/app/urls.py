from django.urls import path
from .import views

urlpatterns = [
    
    path('aboutus', views.aboutus, name='aboutus'),
    path('contact', views.contact, name='contact'),
    path('register', views.register, name='register'),
    path('register_', views.register_, name='register_'),
    path('login', views.loginpage, name='loginpage'),
    path('login_view', views.login_view, name='login_view'),
    path('adminmod/', views.adminmod, name='adminmod'),
    path('unassigned-patients/', views.unassigned_patients_view, name='unassigned_patients'),
    # path('assign_department_and_doctor/<int:patient_id>/', views.assign_department_and_doctor, name='assign_department_and_doctor'),
    path('doctormod',views.doctormod,name='doctormod'),
    path('',views.home,name='home'),
    path('patientmod',views.patientmod,name='patientmod'),
    path('lgout',views.lgout,name='lgout'),
    path('create-department/', views.create_department, name='create_department'),
    path('department_list/', views.department_list, name='department_list'),
    path('delete_department/delete/<int:pk>/', views.delete_department, name='delete_department'),
    path('edit_department/edit/<int:pk>/', views.edit_department, name='edit_department'),
    path('unassigned-doctors/', views.unassigned_doctors_view, name='unassigned_doctors'),
    path('assign_doctor_attributes/<int:doctor_id>/', views.assign_doctor_attributes, name='assign_doctor_attributes'),
    path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('get-doctors-by-department/', views.get_doctors_by_department, name='get_doctors_by_department'),
    path('patient_list/', views.patient_list_view, name='patient_list'),  # List patients by department
    path('view_patient_view/view/<int:patient_id>/', views.view_patient_view, name='view_patient'),  # View patient details
    path('edit_patient_view/edit/<int:patient_id>/', views.edit_patient_view, name='edit_patient'),  # Edit patient details
    path('delete_patient_view/delete/<int:patient_id>/', views.delete_patient_view, name='delete_patient'),  # Delete patient
    path('user_list/', views.user_list_view, name='user_list'),  # List users by department
    path('view_user/view/<int:user_id>/', views.view_user_view, name='view_user'),  # View user details
    path('edit_user/edit/<int:user_id>/', views.edit_user_view, name='edit_user'),  # Edit user details
    path('delete_user/delete/<int:user_id>/', views.delete_user_view, name='delete_user'), # Delete patient
    path('view_user_profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('edit_user_ad/<int:user_id>/edit/', views.edit_user_ad, name='edit_user_ad'),
    #path('view_profile/', views.view_profile, name='view_profile'), 
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),
    path('edit_doctor_profile/edit/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('edit_doctor_profile_submit/edit/submit/', views.edit_doctor_profile_submit, name='edit_doctor_profile_submit'),
    path('patient_list_dr/', views.patient_list_dr, name='patient_list_dr'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('edit_patient_profile/edit/', views.edit_patient_profile, name='edit_patient_profile'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointments_list/', views.appointments_list, name='appointments_list'),
    path('discard_appointment/discard/<int:appointment_id>/', views.discard_appointment, name='discard_appointment'),
    path('approve_appointment/approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('doctor_approved_appointments/appointments/', views.doctor_approved_appointments, name='doctor_approved_appointments'),
    path('doctormod/', views.doctormod, name='doctormod'),
    path('todays-appointments/', views.todays_appointments, name='todays_appointments'),
    path('mark-treated/<int:appointment_id>/', views.mark_treated, name='mark_treated'),
    path('successful_appointments/', views.successful_appointments, name='successful_appointments'),
    path('patient/upcoming-appointments/', views.patient_upcoming_appointments, name='patient_upcoming_appointments'),
    path('patient/successful-appointments/', views.patient_successful_appointments, name='patient_successful_appointments'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('reset_password_/', views.reset_password_, name='reset_password_'),
    path('patient_appointments_status', views.patient_appointments_status, name='patient_appointments_status'),
    path('reset-details/', views.reset_patient_details, name='reset_patient_details'),
    path('get_doctors_by_department/', views.get_doctors_by_department, name='get_doctors_by_department'),
    path('update-patient-stat/<int:patient_id>/', views.update_patient_stat, name='update_patient_stat'),
    
    

]