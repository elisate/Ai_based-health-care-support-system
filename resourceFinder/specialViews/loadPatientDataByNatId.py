from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.treatmentModel import Treatment

@csrf_exempt
def load_patient_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        national_id = data.get("national_id")

        if not national_id:
            return JsonResponse({"error": "national_id is required"}, status=400)

        # Find patient by national_id
        patient = Patient.objects(national_id=national_id).first()
        if not patient:
            return JsonResponse({"error": "No patient found with this national ID"}, status=404)

        # Find all treatments linked to this patient by patient ObjectId
        treatments = Treatment.objects(patient=patient.id)

        # Build response with patient info and treatments
        response = {
            "patient": {
                "patient_id": str(patient.id),
                "firstname": patient.firstname,
                "lastname": patient.lastname,
                "national_id": patient.national_id,
                "gender": patient.gender,
                "age": patient.age,
                "phone": patient.phone,
                "height_cm": patient.height_cm,
                "weight_kg": patient.weight_kg,
                "profile_image": patient.profile_image,
                "treatments": [
                    {
                        "treatment_id": str(t.id),
                        "doctor": {
                            "id": str(t.doctor.id),
                            "name": f"{t.doctor.firstname} {t.doctor.lastname}"
                        },
                        "appointment": str(t.appointment.id) if t.appointment else None,
                        "symptoms": t.symptoms,
                        "diagnosis": t.diagnosis,
                        "prescription": t.prescription,
                        "notes": t.notes,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in treatments
                ]
            }
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        # Log e if needed for debugging
        return JsonResponse({"error": str(e)}, status=500)
