from django.http import JsonResponse
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.patientModel import Patient
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.conf import settings
from datetime import datetime
import json
import jwt
import traceback
from django.views.decorators.http import require_GET
@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        firstname = data.get('firstname', '').strip()
        lastname = data.get('lastname', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '12345678').strip()  # default password if none provided
        national_id = data.get('national_id', '').strip()
        user_role = data.get('userRole', UserRole.PATIENT.value).lower()

        # Basic validation
        if not firstname or not lastname or not email or not national_id:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if not national_id.startswith("1"):
            return JsonResponse({"error": "National ID must start with '1'"}, status=400)

        if user_role not in [role.value for role in UserRole]:
            return JsonResponse({"error": "Invalid userRole"}, status=400)

        # Check unique email and national_id
        if User.objects(email__iexact=email).first():
            return JsonResponse({"error": "Email already registered"}, status=400)

        if User.objects(national_id=national_id).first():
            return JsonResponse({"error": "National ID already registered"}, status=400)

        # Create User
        new_user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=make_password(password),
            national_id=national_id,
            userRole=user_role
        )
        new_user.save()

        # If patient role, create Patient document linked to User
        if user_role == UserRole.PATIENT.value:
            Patient(
                user=new_user,
                firstname=firstname,
                lastname=lastname,
                email=email,
                national_id=national_id
            ).save()

        # Prepare JWT token payload
        payload = {
            "user_id": str(new_user.id),
            "firstname": new_user.firstname,
            "lastname": new_user.lastname,
            "email": new_user.email,
            "userRole": new_user.userRole,
            "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
            "iat": datetime.utcnow()
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return JsonResponse({
            "token": token,
            "user": {
                "user_id": str(new_user.id),
                "firstname": new_user.firstname,
                "lastname": new_user.lastname,
                "email": new_user.email,
                "national_id": new_user.national_id,
                "userRole": new_user.userRole
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@require_GET
def get_all_users(request):
    try:
        users = User.objects()  # Fetch all users
        users_data = []

        for user in users:
            users_data.append({
                "id": str(user.id),
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "national_id": user.national_id,
                "userRole": user.userRole,
            })

        return JsonResponse({"users": users_data}, status=200)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)