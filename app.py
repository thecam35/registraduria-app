from flask import Flask, render_template_string, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Variables de entorno
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql-13049617-thecam35-b71f.d.aivencloud.com'),
    'port': int(os.environ.get('DB_PORT', 15093)),
    'user': os.environ.get('DB_USER', 'avnadmin'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'defaultdb')
}

HTML_TEST = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Conexión</title>
    <style>
        body { font-family: Arial; padding: 50px; text-align: center; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>🧪 Test de Conexión</h1>
    <div id="status">Verificando...</div>
    
    <script>
        fetch('/api/test')
            .then(r => r.json())
            .then(data => {
                const div = document.getElementById('status');
                if (data.success) {
                    div.innerHTML = '<h2 class="success">✅ Conectado a la base de datos!</h2><p>' + data.message + '</p>';
                } else {
                    div.innerHTML = '<h2 class="error">❌ Error de conexión</h2><p>' + data.error + '</p>';
                }
            });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEST)

@app.route('/api/test')
def test():
    try:
        if not DB_CONFIG['password']:
            return jsonify({'success': False, 'error': 'Contraseña no configurada en variables de entorno'})
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 'Conexión exitosa' as message")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': str(result[0])})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
