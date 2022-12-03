from typing import Any
from apiclient import discovery
from models import Generation, Question
from oauth2client.service_account import ServiceAccountCredentials
import os

from dotenv import load_dotenv
load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/forms.body', 'https://www.googleapis.com/auth/drive']
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
KEY_FILE_LOCATION = os.getenv("SERVICE_ACCOUNT_JSON")


class GoogleFormExport:
    creds: ServiceAccountCredentials
    form_service: Any
    drive_service: Any

    def __init__(self):
        # authenticate service account from JSON
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)

        # build Google Forms + Drive services
        self.form_service = discovery.build("forms", "v1", credentials=self.creds, discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)
        self.drive_service = discovery.build("drive", "v3", credentials=self.creds)


    def build_form_info(self, generation: Generation):
        return {
            "info": {
                "title": generation.filename,
                "documentTitle": generation.filename,
            }
        }


    def make_form_quiz(self, form_id):
        update = {
            "requests": [
                {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True
                            }
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                }
            ]
        }

        self.form_service.forms().batchUpdate(formId=form_id, body=update).execute()


    def question_to_json(self, question: Question):
        options = [{ "value": d.text } for d in question.distractors]
        options.append({ "value": question.correct_answer })

        return {
            "title": question.question,
            "questionItem": {
                "question": {
                    "required": True,
                    "grading": {
                        "pointValue": 1,
                        "correctAnswers": {
                            "answers": [
                                {
                                    "value": question.correct_answer
                                }
                            ]
                        }
                    },
                    "choiceQuestion": {
                        "type": "RADIO",
                        "options": options,
                        "shuffle": True
                    }
                }
            }
        }


    def build_question_update(self, question: Question):
        return {
            "requests": [
                {
                    "createItem": {
                        "location": {
                            "index": 0
                        },
                        "item": self.question_to_json(question)
                    }
                }
            ]
        }


    def create_form(self, generation: Generation) -> str:
        # create form with inital info (just the form's title)
        form_info = self.build_form_info(generation)
        form = self.form_service.forms().create(body=form_info).execute() 
        form_id = form["formId"]

        # convert the form to a quiz
        self.make_form_quiz(form_id)

        # add each question to form
        for question in generation.questions:
            question_update = self.build_question_update(question)
            self.form_service.forms().batchUpdate(formId=form_id, body=question_update).execute()
        
        return form_id


    def share_form(self, form_id: str, email: str):
        # create write permission for email
        batch = self.drive_service.new_batch_http_request()
        user_permission = {
            "type": "user",
            "role": "writer",
            "emailAddress": email
        }

        # add permission to form
        batch.add(self.drive_service.permissions().create(fileId=form_id, body=user_permission, fields='id',))
        batch.execute()
