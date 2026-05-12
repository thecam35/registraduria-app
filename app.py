from flask import Flask, render_template_string, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# LEER CONTRASEÑA DE VARIABLES DE ENTORNO (más seguro)
CONFIG_AIVEN = {
    'host': os.environ.get('DB_HOST', 'mysql-13049617-thecam35-b71f.d.aivencloud.com'),
    'port': int(os.environ.get('DB_PORT', 15093)),
    'user': os.environ.get('DB_USER', 'avnadmin'),
    'password': os.environ.get('DB_PASSWORD', ''),  # La contraseña viene de Render
    'database': os.environ.get('DB_NAME', 'defaultdb')
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registraduría Nacional - Sistema de Consulta</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #1a472a 0%, #0d2818 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header h1 span { color: #FFD700; }
        .header p { font-size: 1.1em; }
        .connection-status { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin-top: 15px; }
        .main-layout { display: grid; grid-template-columns: 350px 1fr; gap: 20px; }
        .search-panel { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        .search-section { margin-bottom: 25px; padding: 15px; border-radius: 10px; background: #f8f9fa; }
        .search-section h3 { color: #1a472a; margin-bottom: 15px; border-left: 4px solid #FFD700; padding-left: 10px; }
        .input-group { margin-bottom: 12px; }
        .input-group label { display: block; margin-bottom: 5px; color: #333; font-weight: 500; }
        .input-group input { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; }
        button { width: 100%; padding: 12px; margin-top: 10px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; color: white; }
        .btn-primary { background: #27ae60; }
        .btn-secondary { background: #9b59b6; }
        .btn-warning { background: #e67e22; }
        .btn-danger { background: #95a5a6; }
        .results-panel { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        .results-header { background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .results-container { max-height: 600px; overflow-y: auto; }
        .card { background: white; border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 15px; }
        .card-header { background: #1a472a; color: #FFD700; padding: 12px 15px; font-weight: bold; }
        .card-body { padding: 15px; }
        .info-row { display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
        .info-label { width: 200px; font-weight: bold; color: #555; }
        .info-value { flex: 1; color: #333; }
        .sql-panel { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px; }
        .sql-panel textarea { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-family: monospace; }
        .loading { text-align: center; padding: 40px; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #1a472a; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @media (max-width: 768px) { .main-layout { grid-template-columns: 1fr; } }
        .success { color: #27ae60; }
        .error { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>REGISTRADURÍA NACIONAL <span>EL OJO DE DIOS</span></h1>
            <p>NO HAY NADA OCULTO, ENTRE CIELO Y TIERRA</p>
            <div class="connection-status" id="connectionStatus">
                <span>🔌 Conectando a la base de datos...</span>
            </div>
        </div>
        <div class="main-layout">
            <div class="search-panel">
                <div class="search-section">
                    <h3>🔢 Búsqueda por Cédula</h3>
                    <div class="input-group">
                        <label>Número de Cédula:</label>
                        <input type="text" id="cedulaInput" placeholder="Ingrese número de cédula">
                    </div>
                    <button class="btn-primary" onclick="buscarPorCedula()">🔍 Buscar por Cédula</button>
                </div>
                <div class="search-section">
                    <h3>👤 Búsqueda por Nombres</h3>
                    <div class="input-group">
                        <label>Primer Nombre:</label>
                        <input type="text" id="nombre1Input" placeholder="Primer nombre">
                    </div>
                    <div class="input-group">
                        <label>Segundo Nombre:</label>
                        <input type="text" id="nombre2Input" placeholder="Segundo nombre">
                    </div>
                    <div class="input-group">
                        <label>Primer Apellido:</label>
                        <input type="text" id="apellido1Input" placeholder="Primer apellido">
                    </div>
                    <div class="input-group">
                        <label>Segundo Apellido:</label>
                        <input type="text" id="apellido2Input" placeholder="Segundo apellido">
                    </div>
                    <button class="btn-secondary" onclick="buscarPorNombres()">👥 Buscar por Nombres</button>
                </div>
                <button class="btn-warning" onclick="verTodos()">📋 VER TODOS LOS REGISTROS</button>
                <button class="btn-danger" onclick="limpiarBusqueda()">🗑 LIMPIAR PANTALLA</button>
            </div>
            <div class="results-panel">
                <div class="results-header">
                    <h3>📊 RESULTADOS DE LA BÚSQUEDA</h3>
                    <div class="results-count" id="resultsCount"></div>
                </div>
                <div class="results-container" id="resultsContainer">
                    <div class="loading"><div class="spinner"></div><p>Listo para buscar...</p></div>
                </div>
                <div class="sql-panel">
                    <h3>⚙️ CONSULTA SQL AVANZADA</h3>
                    <textarea id="sqlQuery" rows="3">SELECT * FROM ani LIMIT 10</textarea>
                    <button class="btn-primary" onclick="ejecutarSQL()">▶ EJECUTAR CONSULTA</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        window.onload = function() { verificarConexion(); };
        function verificarConexion() {
            fetch('/api/verificar')
                .then(r => r.json())
                .then(data => {
                    const statusDiv = document.getElementById('connectionStatus');
                    statusDiv.innerHTML = data.connected ? '<span>✅ Conectado a base de datos en nube (Aiven)</span>' : '<span>❌ Error de conexión</span>';
                });
        }
        function buscarPorCedula() {
            const cedula = document.getElementById('cedulaInput').value;
            if (!cedula) { alert('Ingrese un número de cédula'); return; }
            mostrarLoading();
            fetch('/api/buscar/cedula', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({cedula: cedula}) })
                .then(r => r.json()).then(data => mostrarResultados(data)).catch(e => mostrarError(e));
        }
        function buscarPorNombres() {
            const datos = {
                nombre1: document.getElementById('nombre1Input').value,
                nombre2: document.getElementById('nombre2Input').value,
                apellido1: document.getElementById('apellido1Input').value,
                apellido2: document.getElementById('apellido2Input').value
            };
            mostrarLoading();
            fetch('/api/buscar/nombres', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(datos) })
                .then(r => r.json()).then(data => mostrarResultados(data)).catch(e => mostrarError(e));
        }
        function verTodos() {
            mostrarLoading();
            fetch('/api/todos').then(r => r.json()).then(data => mostrarResultados(data)).catch(e => mostrarError(e));
        }
        function ejecutarSQL() {
            const sql = document.getElementById('sqlQuery').value;
            mostrarLoading();
            fetch('/api/ejecutar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sql: sql}) })
                .then(r => r.json()).then(data => mostrarResultados(data)).catch(e => mostrarError(e));
        }
        function limpiarBusqueda() {
            document.getElementById('cedulaInput').value = '';
            document.getElementById('nombre1Input').value = '';
            document.getElementById('nombre2Input').value = '';
            document.getElementById('apellido1Input').value = '';
            document.getElementById('apellido2Input').value = '';
            document.getElementById('sqlQuery').value = 'SELECT * FROM ani LIMIT 10';
            document.getElementById('resultsContainer').innerHTML = '<div class="loading"><div class="spinner"></div><p>Listo para buscar...</p></div>';
            document.getElementById('resultsCount').innerHTML = '';
        }
        function mostrarLoading() {
            document.getElementById('resultsContainer').innerHTML = '<div class="loading"><div class="spinner"></div><p>Cargando...</p></div>';
        }
        function mostrarResultados(data) {
            if (!data.success || data.rows.length === 0) {
                document.getElementById('resultsContainer').innerHTML = '<div class="loading"><p>❌ No se encontraron resultados</p></div>';
                document.getElementById('resultsCount').innerHTML = '<span class="error">0 registros encontrados</span>';
                return;
            }
            let html = '';
            data.rows.forEach((row, index) => {
                html += `<div class="card"><div class="card-header">REGISTRO #${index + 1}</div><div class="card-body">`;
                for (const [key, value] of Object.entries(row)) {
                    let nombreCampo = key;
                    if (key === 'ANINuip') nombreCampo = 'NÚMERO DE CÉDULA';
                    else if (key === 'ANINombre1') nombreCampo = 'PRIMER NOMBRE';
                    else if (key === 'ANINombre2') nombreCampo = 'SEGUNDO NOMBRE';
                    else if (key === 'ANIApellido1') nombreCampo = 'PRIMER APELLIDO';
                    else if (key === 'ANIApellido2') nombreCampo = 'SEGUNDO APELLIDO';
                    else if (key === 'LUGIdExpedicion') nombreCampo = 'LUGAR DE EXPEDICIÓN';
                    else if (key === 'LUGIdNacimiento') nombreCampo = 'LUGAR DE NACIMIENTO';
                    const valorMostrar = value || 'No especificado';
                    html += `<div class="info-row"><div class="info-label">${nombreCampo}:</div><div class="info-value">${valorMostrar}</div></div>`;
                }
                html += `</div></div>`;
            });
            document.getElementById('resultsContainer').innerHTML = html;
            document.getElementById('resultsCount').innerHTML = `<span class="success">✅ ${data.total} registro(s) encontrados | Fuente: NUBE (Aiven)</span>`;
        }
        function mostrarError(error) {
            document.getElementById('resultsContainer').innerHTML = `<div class="loading"><p class="error">❌ Error: ${error}</p></div>`;
        }
    </script>
</body>
</html>
'''

def get_db_connection():
    """Obtener conexión a la base de datos usando variables de entorno"""
    try:
        # Verificar que la contraseña existe
        if not CONFIG_AIVEN['password']:
            print("ERROR: No se encontró la contraseña en variables de entorno")
            return None
            
        conn = mysql.connector.connect(
            host=CONFIG_AIVEN['host'],
            port=CONFIG_AIVEN['port'],
            user=CONFIG_AIVEN['user'],
            password=CONFIG_AIVEN['password'],
            database=CONFIG_AIVEN['database'],
            use_unicode=True,
            charset='utf8mb4',
            connection_timeout=15
        )
        return conn
    except Error as e:
        print(f"Error de conexión: {e}")
        return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/verificar')
def verificar():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'connected': True})
    return jsonify({'connected': False})

@app.route('/api/buscar/cedula', methods=['POST'])
def buscar_cedula():
    data = request.json
    cedula = data.get('cedula', '')
    if not cedula:
        return jsonify({'success': False, 'error': 'Cédula requerida'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'rows': rows, 'total': len(rows)})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/buscar/nombres', methods=['POST'])
def buscar_nombres():
    data = request.json
    condiciones = []
    params = []
    
    if data.get('nombre1'):
        condiciones.append("ANINombre1 LIKE %s")
        params.append(f"%{data['nombre1']}%")
    if data.get('nombre2'):
        condiciones.append("ANINombre2 LIKE %s")
        params.append(f"%{data['nombre2']}%")
    if data.get('apellido1'):
        condiciones.append("ANIApellido1 LIKE %s")
        params.append(f"%{data['apellido1']}%")
    if data.get('apellido2'):
        condiciones.append("ANIApellido2 LIKE %s")
        params.append(f"%{data['apellido2']}%")
    
    if not condiciones:
        return jsonify({'success': False, 'error': 'Ingrese al menos un nombre o apellido'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM ani WHERE {' AND '.join(condiciones)} LIMIT 100"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'rows': rows, 'total': len(rows)})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/todos')
def ver_todos():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani LIMIT 100")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'rows': rows, 'total': len(rows)})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ejecutar', methods=['POST'])
def ejecutar_sql():
    data = request.json
    sql = data.get('sql', '').strip()
    if not sql:
        return jsonify({'success': False, 'error': 'SQL requerido'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        if cursor.description:
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'rows': rows, 'total': len(rows)})
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Consulta ejecutada correctamente'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
