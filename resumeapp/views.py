import json
import base64
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt # Keep this if generate_resume_api is an API endpoint without CSRF in client-side

# Make sure these models are correctly defined in resumeapp/models.py
from .models import UserProfile, Education, Experience, Skill

def resume_builder_view(request):
    """Render the main resume form page"""
    return render(request, 'resumeapp/resume_form.html')

def preview_resume(request):
    """
    Processes the form submission from resume_form.html,
    prepares data, and renders the template selection page (resume_preview.html).
    """
    if request.method == 'POST':
        data = request.POST  # Django's QueryDict for form data
        files = request.FILES  # Django's MultiValueDict for uploaded files

        education_entries = []
        experience_entries = []
        skill_entries = []

        # Process education entries (dynamic number of forms)
        education_count = int(data.get('education_count', 0))
        for i in range(1, education_count + 1):
            education_entries.append({
                'degree': data.get(f'education-{i}-degree', ''),
                'university': data.get(f'education-{i}-university', ''),
                'start_date': data.get(f'education-{i}-startDate', ''),
                'end_date': data.get(f'education-{i}-endDate', ''),
                'description': data.get(f'education-{i}-description', ''),
            })

        # Process experience entries (dynamic number of forms)
        experience_count = int(data.get('experience_count', 0))
        for i in range(1, experience_count + 1):
            experience_entries.append({
                'job_title': data.get(f'experience-{i}-title', ''),
                'company': data.get(f'experience-{i}-company', ''),
                'start_date': data.get(f'experience-{i}-startDate', ''),
                'end_date': data.get(f'experience-{i}-endDate', ''),
                'responsibilities': data.get(f'experience-{i}-responsibilities', ''),
            })

        # Process skill entries (dynamic number of forms)
        skill_count = int(data.get('skill_count', 0))
        for i in range(1, skill_count + 1):
            skill_entries.append({
                'name': data.get(f'skill-{i}-name', ''),
            })

        # Handle Profile Picture: Convert to Base64 for HTML preview and PDF
        profile_picture_base64 = None
        profile_picture_file = files.get('profilePicture')
        if profile_picture_file:
            try:
                # Read the file content and encode it in base64
                encoded_image = base64.b64encode(profile_picture_file.read()).decode('utf-8')
                # Create a data URI string for direct embedding in HTML/PDF
                profile_picture_base64 = f"data:{profile_picture_file.content_type};base64,{encoded_image}"
            except Exception as e:
                print(f"Error encoding profile picture: {e}")
                profile_picture_base64 = None # Fallback if encoding fails

        # Prepare context to pass to the resume_preview.html template
        context = {
            'fullName': data.get('fullName', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'linkedin': data.get('linkedin', ''),
            'address': data.get('address', ''),
            'summary': data.get('summary', ''),
            'education_entries': education_entries,
            'experience_entries': experience_entries,
            'skill_entries': skill_entries,
            'profile_picture_base64': profile_picture_base64, # Used by included templates for preview
            
            # This is crucial: Pass all original form data (as a dict) for re-submission
            # via hidden inputs in the download forms on resume_preview.html
            'original_form_data': data.dict(), 
            'profile_picture_base64_for_download': profile_picture_base64, # Re-pass base64 for PDF download
        }

        # Render the main template selection page
        return render(request, 'resumeapp/resume_preview.html', context)
    return HttpResponse("Invalid method for preview_resume. Please submit via POST.", status=405)


def download_pdf(request):
    """
    Generates and downloads a PDF version of the resume
    based on the template selected by the user on the preview page.
    """
    if request.method == 'POST':
        data = request.POST # Data containing all resume info and selected template name

        # Get the selected template name from the hidden input field
        template_name = data.get('template_name', 'resume_template_modern.html') # Default template

        # Re-parse the data from the POST request (since it's a new POST from preview page)
        education_entries = []
        experience_entries = []
        skill_entries = []

        education_count = int(data.get('education_count', 0))
        for i in range(1, education_count + 1):
            education_entries.append({
                'degree': data.get(f'education-{i}-degree', ''),
                'university': data.get(f'education-{i}-university', ''),
                'start_date': data.get(f'education-{i}-startDate', ''),
                'end_date': data.get(f'education-{i}-endDate', ''),
                'description': data.get(f'education-{i}-description', ''),
            })

        experience_count = int(data.get('experience_count', 0))
        for i in range(1, experience_count + 1):
            experience_entries.append({
                'job_title': data.get(f'experience-{i}-title', ''),
                'company': data.get(f'experience-{i}-company', ''),
                'start_date': data.get(f'experience-{i}-startDate', ''),
                'end_date': data.get(f'experience-{i}-endDate', ''),
                'responsibilities': data.get(f'experience-{i}-responsibilities', ''),
            })
        
        skill_count = int(data.get('skill_count', 0))
        for i in range(1, skill_count + 1):
            skill_entries.append({
                'name': data.get(f'skill-{i}-name', ''),
            })

        # Get the base64 encoded profile picture string
        profile_picture_base64 = data.get('profile_picture_base64_for_download', None)
        
        # Prepare context for the selected template for PDF rendering
        context = {
            'fullName': data.get('fullName', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'linkedin': data.get('linkedin', ''),
            'address': data.get('address', ''),
            'summary': data.get('summary', ''),
            'education_entries': education_entries,
            'experience_entries': experience_entries,
            'skill_entries': skill_entries,
            'profile_picture_base64': profile_picture_base64, # Pass to the template for PDF rendering
        }

        # Render the selected template to HTML string
        # Ensure the template_name is safe and corresponds to an actual template file
        template_path = f'resumeapp/{template_name}'
        html = render_to_string(template_path, context)

        # Create a Django HttpResponse with PDF content type
        response = HttpResponse(content_type='application/pdf')
        # Suggest a filename for the downloaded PDF
        filename_prefix = template_name.replace('resume_template_', '').replace('.html', '')
        response['Content-Disposition'] = f'attachment; filename=resume_{filename_prefix}.pdf'

        # Use xhtml2pdf to create the PDF from the HTML string
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            # If there's an error during PDF generation
            return HttpResponse(f"Error generating PDF: {pisa_status.err}", status=500)
        
        return response
    return HttpResponse("Invalid request method for download_pdf. Please submit via POST.", status=405)


# This view saves data to the database. It might be called via AJAX.
# If it's an API endpoint and CSRF token isn't handled client-side, @csrf_exempt is needed.
# For standard Django forms, remove @csrf_exempt and ensure {% csrf_token %} is in the form.
@csrf_exempt
def generate_resume_api(request):
    """API endpoint to save resume data to database"""
    if request.method == 'POST':
        try:
            post_data = request.POST
            profile_picture_file = request.FILES.get('profilePicture')

            # Get or create user and profile (assuming a generic user for now)
            user, _ = User.objects.get_or_create(username='current_resume_user')
            user_profile, _ = UserProfile.objects.get_or_create(user=user)

            # Update basic profile info
            user_profile.full_name = post_data.get('fullName', '')
            user_profile.email = post_data.get('email', '')
            user_profile.phone_number = post_data.get('phone', '')
            user_profile.linkedin_url = post_data.get('linkedin', '')
            user_profile.address = post_data.get('address', '')
            user_profile.summary = post_data.get('summary', '')

            # Handle profile picture upload/update for the UserProfile model
            if profile_picture_file:
                user_profile.profile_picture = profile_picture_file
            # If an image was previously there but now nothing is uploaded, clear it
            elif 'profilePicture' in request.FILES and not profile_picture_file:
                user_profile.profile_picture = None

            user_profile.save()

            # Clear existing related entries to avoid duplicates on update
            Education.objects.filter(user_profile=user_profile).delete()
            Experience.objects.filter(user_profile=user_profile).delete()
            Skill.objects.filter(user_profile=user_profile).delete()

            # Process and save education entries
            education_count = int(post_data.get('education_count', 0))
            for i in range(1, education_count + 1):
                degree = post_data.get(f'education-{i}-degree')
                university = post_data.get(f'education-{i}-university')
                if degree and university:  # Only create if essential fields are present
                    Education.objects.create(
                        user_profile=user_profile,
                        degree=degree,
                        university=university,
                        start_date=post_data.get(f'education-{i}-startDate', ''),
                        end_date=post_data.get(f'education-{i}-endDate', ''),
                        description=post_data.get(f'education-{i}-description', '')
                    )

            # Process and save experience entries
            experience_count = int(post_data.get('experience_count', 0))
            for i in range(1, experience_count + 1):
                title = post_data.get(f'experience-{i}-title')
                company = post_data.get(f'experience-{i}-company')
                if title and company:  # Only create if essential fields are present
                    Experience.objects.create(
                        user_profile=user_profile,
                        job_title=title,
                        company=company,
                        start_date=post_data.get(f'experience-{i}-startDate', ''),
                        end_date=post_data.get(f'experience-{i}-endDate', ''),
                        responsibilities=post_data.get(f'experience-{i}-responsibilities', '')
                    )

            # Process and save skill entries
            skill_count = int(post_data.get('skill_count', 0))
            for i in range(1, skill_count + 1):
                skill_name = post_data.get(f'skill-{i}-name')
                if skill_name:  # Only create if skill name exists
                    Skill.objects.create(
                        user_profile=user_profile,
                        name=skill_name
                    )

            # Prepare JSON response
            profile_image_url = user_profile.profile_picture.url if user_profile.profile_picture else None

            return JsonResponse({
                'message': 'Resume data and profile picture saved successfully!',
                'profile_image_url': profile_image_url,
                'user_profile_id': user_profile.id
            })

        except Exception as e:
            print(f"Error processing resume data: {e}")
            return JsonResponse({'error': str(e), 'details': str(e)}, status=500) # Include details for debugging

    return HttpResponse("Invalid request method for generate_resume_api. Please submit via POST.", status=405)