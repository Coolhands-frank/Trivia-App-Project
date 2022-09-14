import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    """
    @Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @Done: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS, PUT')
        return response
    
    """
    @Done:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            category_dictionary = {}
            for category in categories:
                category_dictionary[category.id] = category.type
        
            return jsonify({
                'success': True, 
                'categories': category_dictionary
            })
        except:
            abort(422)
            
    """
    @Done:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.all()
            formated_questions = [question.format() for question in questions]
            categories = Category.query.all()
            category_dictionary = {} #creats a category dictionary and populate it with key category.id from Category database table
            for category in categories:
                category_dictionary[category.id] = category.type
            
            if len(formated_questions[start:end]) == 0:
                abort(404)
            
            return jsonify({
                "success": True, 
                "questions": formated_questions[start:end],
                "total_questions": len(formated_questions),
                "current_category": None,
                "categories": category_dictionary
            })
        except:
            abort(404)
        
    """
    @Done:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def question_delete(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.all()
            formated_questions = [question.format() for question in questions]
            
            if question is None:
                abort(404)
                
            question.delete()
            
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        
        except:
            abort(422)

    """
    @Done:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search_term = body.get('searchTerm', None)
        
        try: 
            
            if search_term:
                search_questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
                page = request.args.get('page', 1, type=int)
                start = (page - 1) * QUESTIONS_PER_PAGE
                end = start + QUESTIONS_PER_PAGE
                search_questions = [question.format() for question in search_questions]
                
                return jsonify({
                    'success': True,
                    'questions': search_questions[start:end],
                    'totalQuestions': len(search_questions)
                })
            
            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            
                question.insert()
            
                return jsonify({
                    'success': True
                })
        except:
            abort(422)
            
     # the search and create question endpoint uses same route "/questions"   
    
    """
    @Done:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
         
    """
    @Done:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category>/questions', methods=['GET'])
    def get_questions_by_cat_id(category):
        try:
            quest_category = Question.query.order_by(Question.id).filter(Question.category==category).all()
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE    
            cat_questions = [question.format() for question in quest_category]
            
            if quest_category is None:
                abort(404)
            
            return jsonify({
                'success': True, 
                'questions': cat_questions[start:end],
                'totalQuestions': len(cat_questions),
                'currentCategory': category
            })
        
        except:
            abort(422)
           
    
    """
    @Done:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        try:
            body = request.get_json()
            category = body.get('quiz_category', None)
            previous_questions = body.get('previous_questions', None)
            
            category_id = category["id"]
            if category_id:
                start_quiz = Question.query.filter(Question.id.notin_(previous_questions),Question.category == category['id']).all()
                format_quiz = [question.format() for question in start_quiz]
                
            else:
                start_quiz = Question.query.filter(Question.id.notin_(previous_questions)).all()
                format_quiz = [question.format() for question in start_quiz]
            
            if not format_quiz:
                current_question = None
                return jsonify({
                    'success': True
                })
            else:
                current_question = random.choice(format_quiz)
            
            return jsonify({
                'success': True,
                'question': current_question
            })
        except:
            abort(422)
                
    """
    @Done:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False, 
            'error': 422,
            'message': 'unprocessable'
        }), 422
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not allowed"
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "Internal Server Error"
        }), 500

    return app
