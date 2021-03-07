from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)
#Ajouter la database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memo.db'
db = SQLAlchemy(app)

#Table database pour stocker les traductions du mémo
class Translator(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   french_word = db.Column(db.String(200), nullable=False)
   english_word = db.Column(db.String(200), nullable=False)

   def __repr__(self):
      return '<Word %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
   if request.method == 'POST':
      #Récupérer le formulaire dans des variables
      french_translate = request.form['traduction-francais']
      english_translate = request.form['traduction-anglais']

      #Ajouter une majuscule au début des mots
      french_translate = str(french_translate).capitalize()
      english_translate = str(english_translate).capitalize()

      #Créer l'objet translator
      new_word = Translator(french_word=french_translate, english_word=english_translate)

      #Requete pour ajouter le mot à la database
      try:
         db.session.add(new_word)
         db.session.commit()
         return redirect('/') #Redirige vers la homepage
      except:
         return "Une erreur est survenue lors de l'ajout de la traduction"
   else:
      #Récupérer toutes les traductions de la database
      traductions = Translator.query.order_by(Translator.french_word).all()
      return render_template('index.html', traductions=traductions) #Transfère les traductions vers la page


#Supprimer une traduction
@app.route('/delete/<int:id>')
def delete(id):
   #Récupérer la traduction à supprimer
   word_to_delete = Translator.query.get_or_404(id)

   try:
      db.session.delete(word_to_delete)
      db.session.commit()
      return redirect('/')
   except:
      return 'Une erreur est survenue lors de la suppression de la traduction'


#Modifier une traduction
@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
   # Récupérer la traduction à modifier
   traduction = Translator.query.get_or_404(id)

   #Update de la traduction
   if request.method == 'POST':
      #Récupérer les modifications
      french_update = request.form['traduction-francais']
      english_update = request.form['traduction-anglais']

      # Modifier l'objet récupéré avec les data du form
      traduction.french_word = str(french_update).capitalize()
      traduction.english_word = str(english_update).capitalize()

      # Commit les modifications de l'objet
      try:
         db.session.commit()
         return redirect('/')
      except:
         return "Une erreur est survenue lors de la modification de la traduction"
   else:
      return render_template('update.html', traduction=traduction)


#Quiz -> Trouver la traduction des mots français
@app.route('/quiz')
def quiz_fr_to_en():
   #Récupérer toutes les traductions
   traductions = Translator.query.order_by(Translator.french_word).all()
   memo_length = len(traductions)-1

   #Générer un nombre aléatoire
   random_int = randint(0, memo_length)

   try:
      answer_attempts = request.args.get('answer')
   except:
      print("Pas d'argument trouvé")

   #Récupérer la traduction qui a pour id le random_int
   try:
      random_traduction = traductions[random_int]
      return render_template('quiz_fr.html', random_traduction=random_traduction, answer_attempts=answer_attempts)
   except:
      return "Aucun mot n'a été trouvé !"


#Réponse du quiz french to english
@app.route('/quiz/answer/<int:id>', methods=['POST', 'GET'])
def answer_fr_to_en(id):
   #Récupérer la traduction du test
   traduction_test = Translator.query.get_or_404(id)

   #Récupérer la réponse de l'utilisateur
   answer_english = request.form['traduction-anglais']

   #Ignorer la casse
   traduction_answer = str(traduction_test.english_word).lower()
   answer_english = str(answer_english).lower()

   try:
      answer_attempts = int(request.args.get('answer'))
      print(answer_attempts)
      answer_attempts -= 1
      print(answer_attempts)
   except:
      print("Pas d'argument trouvé")

   #Corriger la réponse
   if traduction_answer != answer_english and 3 > answer_attempts > 0:
      return render_template('quiz_fr.html', random_traduction=traduction_test, answer_attempts=str(answer_attempts))
   else:
      return redirect('/quiz?answer=3')



if __name__ == "__main__":
   app.run(debug=True)