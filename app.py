import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration de la base de données et des fichiers
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SECRET_KEY'] = 'cle_secrete_voltconnect_2026'

db = SQLAlchemy(app)

# Création du dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Modèle de données pour les livres/PDF
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    fichier = db.Column(db.String(200), nullable=False)

# Création de la base de données au démarrage
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# --- SECTION CALCULATEUR TECHNIQUE ---
@app.route('/calculateur', methods=['POST'])
def calculateur():
    try:
        tension = float(request.form.get('tension', 230))
        courant = float(request.form.get('courant', 16))
        longueur = float(request.form.get('longueur', 10))
        conducteur = request.form.get('conducteur', 'cuivre')
        
        rho = 0.0179 if conducteur == 'cuivre' else 0.029
        chute_max_volt = tension * 0.03
        section_theorique = (2 * rho * longueur * courant) / chute_max_volt
        
        sections_standards = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50]
        section_recommandee = sections_standards[-1]
        for s in sections_standards:
            if s >= section_theorique:
                section_recommandee = s
                break
                
        resultat = {
            'section_theorique': round(section_theorique, 2),
            'section_recommandee': section_recommandee
        }
    except ValueError:
        resultat = {'erreur': 'Veuillez entrer des valeurs numériques valides.'}
        
    return render_template('index.html', resultat=resultat)

# --- SECTION BIBLIOTHÈQUE & PDF ---
@app.route('/bibliotheque')
def bibliotheque():
    documents = Document.query.all()
    return render_template('bibliotheque.html', documents=documents)

@app.route('/ajouter-pdf', methods=['POST'])
def ajouter_pdf():
    titre = request.form.get('titre')
    description = request.form.get('description')
    file = request.files.get('fichier')
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        nouveau_doc = Document(titre=titre, description=description, fichier=filename)
        db.session.add(nouveau_doc)
        db.session.commit()
        
    return redirect(url_for('bibliotheque'))

@app.route('/telecharger/<filename>')
def telecharger_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
                   
