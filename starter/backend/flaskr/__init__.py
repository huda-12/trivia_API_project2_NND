import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# pagination (every 10 questions). 
def paginate_questions(request , selection):
    page = request.args.get('page' ,1 ,type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  CORS(app)
    # resources={r"/api/*":{"origins": "*"}})
  
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'PUT,GET,PATCH,POST,DELETE,OPTIONS')
    return response
  '''
  _________________________GET categories___________________________
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories') 
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    formatted_categories = [category.format() for category in categories ]
    if len(categories) == 0 :
      abort(404)

    return jsonify({
      'success':True,
      'categories':{category.id: category.type for category in categories} 
      # formatted_categories #{category.id: category.type for category in categories} 
      })
  
  '''
  ______________________________GET questions __________________________________________
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions,( current category, categories.) 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,selection)
     

    categories = Category.query.order_by(Category.type).all()
    # formatted_categories = [category.format() for category in categories ]

    if len (current_questions) == 0 :
        abort(404)


    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions' : len(Question.query.all()),
      'categories' : {category.id: category.type for category in categories},
      'current_category' :None 
      })
    

#   '''
#   TEST: At this point, when you start the application
#   you should see questions and categories generated,
#   ten questions per page and pagination at the bottom of the screen for three pages.
#   Clicking on the page numbers should update the questions. 
#   '''


# #_________________________________DELETE METHOD________________________________________________
#   # @TODO: 
#   # Create an endpoint to DELETE question using a question ID. 
  @app.route('/questions/<int:question_id>' , methods=['DELETE'])
  def delete_questions(question_id):
    try: # query find id 

      question = Question.query.get(question_id)


      question.delete()
      # selection = Question.query.order_by(Question.id).all()
      # current_questions = paginate_questions(request,selection)
 
      return jsonify({
        'success':True, 
        'deleted':question.id ,
        # 'questions' :current_questions ,
        # 'total_questions': len(Question.query.all())
        })

    except:
      abort (422)

#   # TEST: When you click the trash icon next to a question, the question will be removed.
#   # This removal will persist in the database and when you refresh the page. 
#   '''      
#_____________________________POST method_____________________________________

#   # '''
#   # @TODO: 
#   # Create an endpoint to POST a new question, 
#   # which will require the question and answer text, 
#   # category, and difficulty score.

  @app.route('/questions', methods=['POST'])
  def create_question():

    # get from front end use json 
    data = request.get_json()
    new_question = data.get('question' ,None)
    new_answer = data.get('answer' ,None)
    new_category = data.get('category' ,None)
    new_difficulty = data.get('difficulty' ,None)

    try:
        #  insert to database 
      question = Question(question=new_question, answer=new_answer, category=new_category , difficulty=new_difficulty )
      question.insert()
        # paginate_questions
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success':True, 
        'created': question.id ,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


#   # TEST: When you submit a question on the "Add" tab, 
#   # the form will clear and the question will appear at the end of the last page
#   # of the questions list in the "List" tab.  
#   # '''
#_____________________________POST methods search________________________________________________
#   # '''
#   # @TODO: 
#   # Create a POST endpoint to get questions based on a search term. 
#   # It should return any questions for whom the search term 
#   # is a substring of the question. 
  @app.route('/questions/search', methods=['POST']) 
  def search_question():
    # get from front end use json 
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term:
        search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()

        return jsonify({
              'success': True,
              'questions': [question.format() for question in search_results],
              'total_questions': len(search_results),
             
         })
    abort(404)
#   # TEST: Search by any phrase. The questions list will update to include 
#   # only question that include that string within their question. 
#   # Try using the word "title" to start. 
#   # '''
#_________________________________________ GET methods based on category._______________________________
#   # '''
#   # @TODO: 
#   # Create a GET endpoint to get questions based on category. 
  @app.route('/categories/<int:category_id>/questions', methods=['GET']) 
  def retrieve_questions_by_category(category_id):

      try:
          category = Category.query.filter(Category.id == category_id).one_or_none()
          questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()

          return jsonify({
              'success': True,
              'questions': [question.format() for question in questions],
              'total_questions': len(questions),
              'current_category': category.type
          })
      except:
          abort(404)

  
  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  # # '''
  # _________________________________________ POST methods quizzes_________________________________
  # '''
  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 
  @app.route('/quizzes', methods=['POST'])
  def ranom_play_quiz():


    try:
        body = request.get_json()

        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(422)
        #take category and previous question parameters 
        category = body.get('quiz_category') # type,id  for Category   ex:(Art ,2)
        previous_questions = body.get('previous_questions') #array
        
        # if all category is selected
        if category['type'] == 'click':
            available = Question.query.filter(Question.id.notin_((previous_questions))).all()
        else:
            available = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()
        # refrence https://www.w3schools.com/python/ref_random_randrange.asp explian rrandom.andrange
        new_question = available[random.randrange( #random.randrange(start, stop, step) 
            0, len(available))].format() if len(available) > 0 else None
        # start from 0 and stop until length available  if it >0 
        return jsonify({
            'success': True,
            'question': new_question
         })
    except:
        abort(422)  


  
#   # TEST: In the "Play" tab, after a user selects "All" or a category,
#   # one question at a time is displayed, the user is allowed to answer
#   # and shown whether they were correct or not. 
#   # '''


#   # '''
#   # @TODO: 
# #   # Create error handlers for all expected errors 
# # #   # including 404 and 422. 
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
           'success': False,
           'error': 404,
           'message': "resource not found"
        }),404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
         'success': False,
         'error': 422,
         'message': "unprocessable"
        }),422
      
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
         'success': False,
         'error': 400,
         'message': "bad request"
      }),400

  @app.errorhandler(405)
  def not_found(error):
      return jsonify({
         'success': False,
         'error': 405,
         'message': "method not allowed"
      }),405


    
  return app

    #   