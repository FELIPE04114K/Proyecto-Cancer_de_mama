import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Asegura que matplotlib no use la GUI
import matplotlib.pyplot as plt
from flask import Flask, send_file, render_template, request
import os

# Asegúrate de que la carpeta 'static' exista para guardar las imágenes generadas
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None

    # Verifica si se han recibido datos en el formulario
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            imc = float(request.form['imc'])
            glucosa = float(request.form['glucosa'])
            insulina = float(request.form['insulina'])

            # Lógica para determinar el riesgo de cáncer de mama
            if imc >= 30 and glucosa > 100 and insulina > 20:
                resultado = "!Advertencia¡ , con base a los datos que tenemos acceso deberia ir con un doctor para revisar esos sintomas."
            elif imc >= 30 or glucosa > 100 or insulina > 20:
                resultado = "Tienes que tener cuidado, tienes algunos factores muy elevados, consulte a su médico para asegurarse."
            else:
                resultado = "Los sintomas no demuestran posibilidad de cancer de mama."
        except ValueError:
            resultado = "Por favor, ingresa valores válidos."

    # Cargar los datos del archivo Excel
    try:
        df = pd.read_excel("BaseDeDatos.xlsx")
    except Exception as e:
        resultado = f"Error al cargar el archivo: {e}"

    # Asegúrate de que la carpeta 'static' exista
    if not os.path.exists('static'):
        os.makedirs('static')

    # Definir las columnas y sus descripciones
    columnas = [
        "Índice de Masa Corpora", "Glucosa", "Insulina", "HOMA", 
        "Leptina", "Adiponectina", "Resistina", "Proteína MCP-1", "Clasificación"
    ]

    descripciones = {
        "Índice de Masa Corpora": "Un índice de masa corporal (IMC) de 30 o más, considerado clínicamente como obesidad, se ha relacionado con efectos negativos significativos en la salud, particularmente en el contexto del cáncer de mama. La obesidad promueve un entorno inflamatorio crónico en el cuerpo, lo cual puede alterar la función normal del sistema inmunológico y favorecer un ambiente propicio para el desarrollo y progresión del cáncer. Además, se ha observado que el exceso de grasa corporal puede estimular mutaciones genéticas en las células mamarias, aumentando así el riesgo de aparición del cáncer.",
        "Glucosa": "Las células cancerosas, incluyendo las del cáncer de mama, presentan un metabolismo alterado que las lleva a consumir glucosa (azúcar) a una velocidad mucho mayor que las células normales. Este fenómeno, conocido como el efecto Warburg, ocurre porque las células cancerosas dependen en gran medida de la glucólisis, un proceso que les permite obtener energía rápidamente, incluso en ausencia de oxígeno. Esta alta demanda energética está relacionada con su rápido crecimiento y proliferación.",
        "Insulina": "La resistencia a la insulina, una condición en la que las células del cuerpo no responden adecuadamente a esta hormona, puede aumentar el riesgo de desarrollar cáncer de mama. Cuando se presenta esta resistencia, el organismo compensa produciendo más insulina, lo que da lugar a niveles elevados en sangre tanto de insulina como del factor de crecimiento insulínico tipo 1 (IGF-1).",
        "HOMA": "Se ha demostrado que la resistencia a la insulina, evaluada mediante el índice HOMA (Homeostasis Model Assessment), está asociada con un mayor riesgo de desarrollar cáncer de mama, particularmente en mujeres posmenopáusicas. Este índice permite estimar la función de la insulina y la sensibilidad del organismo a esta hormona a partir de los niveles de glucosa e insulina en ayunas.",
        "Leptina": "La leptina, una hormona producida principalmente por el tejido adiposo, desempeña un papel clave en la regulación del apetito y el metabolismo energético. Sin embargo, en el contexto del cáncer de mama, se ha observado que niveles elevados de leptina —frecuentemente presentes en personas con sobrepeso u obesidad— pueden tener efectos adversos.",
        "Adiponectina": "La adiponectina es una hormona producida por los adipocitos (células del tejido graso) que cumple funciones antiinflamatorias, antioxidantes y sensibilizadoras a la insulina. A diferencia de otras hormonas relacionadas con la obesidad, como la leptina, la adiponectina parece tener un efecto protector frente al desarrollo de diversos tipos de cáncer, incluido el cáncer de mama.",
        "Resistina": "La resistina es una proteína inflamatoria que se secreta principalmente por los adipocitos y los monocitos/macrófagos. Originalmente relacionada con la resistencia a la insulina y la obesidad, investigaciones más recientes han evidenciado su implicación en procesos asociados al cáncer, incluyendo el cáncer de mama.",
        "Proteína MCP-1": "La proteína quimioatrayente de monocitos-1, conocida como MCP-1 o CCL2, es una citocina proinflamatoria que desempeña un papel clave en la regulación de la respuesta inmune al atraer monocitos y otras células del sistema inmunológico hacia los tejidos inflamados. En el contexto del cáncer de mama, MCP-1 ha sido identificada como un factor que contribuye de manera significativa a la progresión tumoral.",
        "Clasificación": "El cáncer de mama se clasifica en distintos tipos según varios criterios que permiten entender mejor su comportamiento, pronóstico y las opciones de tratamiento más adecuadas. Una de las principales formas de clasificación se basa en características moleculares y celulares del tumor."
    }

    # Generar gráficos para cada columna
    for columna in columnas:
        if columna in df.columns:
            plt.figure(figsize=(10, 6))
            if df[columna].dtype == 'object':  # Si es una columna categórica
                df[columna].value_counts().plot(kind='bar', color='#de4c8a', edgecolor='black')
                plt.title(f"Distribución de {columna}")
                plt.xlabel(columna)
                plt.ylabel("Frecuencia")
            else:  # Si es una columna numérica
                plt.hist(df[columna], bins=15, color='#de4c8a', edgecolor='black')
                plt.title(f"Distribución de {columna}")
                plt.xlabel(columna)
                plt.ylabel("Frecuencia")
            plt.grid(True)

            # Guardar la imagen generada en la carpeta 'static'
            image_name = f'{columna.replace(" ", "_")}.png'
            image_path = os.path.join(app.config['STATIC_FOLDER'], image_name)
            plt.savefig(image_path, format="png")
            plt.close()

    # Renderizar la plantilla con las columnas, descripciones y resultado
    return render_template("index.html", columnas=columnas, descripciones=descripciones, resultado=resultado)

@app.route('/static/<filename>')
def obtener_imagen(filename):
    # Ruta para servir las imágenes generadas
    return send_file(os.path.join(app.config['STATIC_FOLDER'], filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
