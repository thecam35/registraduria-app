from flask import Flask, render_template_string, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# Configuración desde variables de entorno
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql-13049617-thecam35-b71f.d.aivencloud.com'),
    'port': int(os.environ.get('DB_PORT', 15093)),
    'user': os.environ.get('DB_USER', 'avnadmin'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'defaultdb'),
    'use_unicode': True,
    'charset': 'utf8mb4'
}

HTML_COMPLETO = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registraduría Nacional - Sistema de Consulta</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .header { 
            background: linear-gradient(135deg, #1a472a 0%, #0d2818 100%); 
            color: white; 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 30px; 
            text-align: center; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header h1 span { color: #FFD700; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        
        .connection-status { 
            background: rgba(255,255,255,0.1); 
            padding: 10px; 
            border-radius: 10px; 
            margin-top: 15px; 
            font-size: 0.9em; 
        }
        
        .main-layout { display: grid; grid-template-columns: 350px 1fr; gap: 20px; }
        
        .search-panel { 
            background: white; 
            border-radius: 15px; 
            padding: 20px; 
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); 
            height: fit-content; 
        }
        
        .search-section { 
            margin-bottom: 25px; 
            padding: 15px; 
            border-radius: 10px; 
            background: #f8f9fa; 
        }
        
        .search-section h3 { 
            color: #1a472a; 
            margin-bottom: 15px; 
            font-size: 1.2em; 
            border-left: 4px solid #FFD700; 
            padding-left: 10px; 
        }
        
        .input-group { margin-bottom: 12px; }
        
        .input-group label { 
            display: block; 
            margin-bottom: 5px; 
            color: #333; 
            font-weight: 500; 
            font-size: 0.9em; 
        }
        
        .input-group input { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #e0e0e0; 
            border-radius: 8px; 
            font-size: 14px; 
            transition: all 0.3s; 
        }
        
        .input-group input:focus { 
            outline: none; 
            border-color: #1a472a; 
        }
        
        button { 
            width: 100%; 
            padding: 12px; 
            margin-top: 10px; 
            border: none; 
            border-radius: 8px; 
            font-size: 14px; 
            font-weight: bold; 
            cursor: pointer; 
            transition: all 0.3s; 
            color: white; 
        }
        
        .btn-primary { background: #27ae60; }
        .btn-primary:hover { background: #219a52; transform: translateY(-2px); }
        
        .btn-secondary { background: #9b59b6; }
        .btn-secondary:hover { background: #8e44ad; transform: translateY(-2px); }
        
        .btn-warning { background: #e67e22; }
        .btn-warning:hover { background: #d35400; transform: translateY(-2px); }
        
        .btn-danger { background: #95a5a6; }
        .btn-danger:hover { background: #7f8c8d; transform: translateY(-2px); }
        
        .btn-info { background: #3498db; }
        .btn-info:hover { background: #2980b9; transform: translateY(-2px); }
        
        .results-panel { 
            background: white; 
            border-radius: 15px; 
            padding: 20px; 
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); 
        }
        
        .results-header { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px; 
        }
        
        .results-header h3 { color: #1a472a; margin-bottom: 10px; }
        .results-count { color: #666; font-size: 0.9em; }
        
        .results-container { max-height: 600px; overflow-y: auto; }
        
        .card { 
            background: white; 
            border: 1px solid #e0e0e0; 
            border-radius: 10px; 
            margin-bottom: 15px; 
            overflow: hidden; 
            transition: all 0.3s; 
        }
        
        .card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        
        .card-header { 
            background: #1a472a; 
            color: #FFD700; 
            padding: 12px 15px; 
            font-weight: bold; 
        }
        
        .card-body { padding: 15px; }
        
        .info-row { 
            display: flex; 
            padding: 8px 0; 
            border-bottom: 1px solid #f0f0f0; 
        }
        
        .info-row:last-child { border-bottom: none; }
        
        .info-label { 
            width: 200px; 
            font-weight: bold; 
            color: #555; 
        }
        
        .info-value { flex: 1; color: #333; }
        
        .sql-panel { 
            margin-top: 20px; 
            padding: 15px; 
            background: #f8f9fa; 
            border-radius: 10px; 
        }
        
        .sql-panel h3 { 
            color: #1a472a; 
            margin-bottom: 10px; 
            font-size: 1em; 
        }
        
        .sql-panel textarea { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #e0e0e0; 
            border-radius: 8px; 
            font-family: 'Courier New', monospace; 
            font-size: 12px; 
            resize: vertical; 
            margin-bottom: 10px; 
        }
        
        .loading { text-align: center; padding: 40px; }
        
        .spinner { 
            border: 4px solid #f3f3f3; 
            border-top: 4px solid #1a472a; 
            border-radius: 50%; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto; 
        }
        
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        
        @media (max-width: 768px) { 
            .main-layout { grid-template-columns: 1fr; } 
            .header h1 { font-size: 1.5em; }
            .info-label { width: 120px; font-size: 12px; }
            .info-value { font-size: 12px; }
        }
        
        .success { color: #27ae60; }
        .error { color: #e74c3c; }
        
        .footer-note { 
            text-align: center; 
            margin-top: 20px; 
            padding: 15px; 
            color: #666; 
            font-size: 12px; 
            border-top: 1px solid #e0e0e0; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>REGISTRADURÍA NACIONAL <span>EL OJO DE DIOS</span></h1>
            <p>NO HAY NADA OCULTO, ENTRE CIELO Y TIERRA</p>
            <div class="connection-status" id="connectionStatus">
                <span>🔌 Verificando conexión...</span>
            </div>
        </div>
        
        <div class="main-layout">
            <!-- Panel izquierdo - Búsqueda -->
            <div class="search-panel">
                <div class="search-section">
                    <h3>🔢 Búsqueda por Cédula</h3>
                    <div class="input-group">
                        <label>Número de Cédula:</label>
                        <input type="text" id="cedulaInput" placeholder="Ingrese número de cédula" onkeypress="if(event.key==='Enter') buscarPorCedula()">
                    </div>
                    <button class="btn-primary" onclick="buscarPorCedula()">🔍 Buscar por Cédula</button>
                </div>
                
                <div class="search-section">
                    <h3>👤 Búsqueda por Nombres y Apellidos</h3>
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
            
            <!-- Panel derecho - Resultados -->
            <div class="results-panel">
                <div class="results-header">
                    <h3>📊 RESULTADOS DE LA BÚSQUEDA</h3>
                    <div class="results-count" id="resultsCount"></div>
                </div>
                <div class="results-container" id="resultsContainer">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Listo para buscar...</p>
                    </div>
                </div>
                
                <!-- Panel SQL Avanzado -->
                <div class="sql-panel">
                    <h3>⚙️ CONSULTA SQL AVANZADA</h3>
                    <textarea id="sqlQuery" rows="3" placeholder="SELECT * FROM ani LIMIT 10">SELECT * FROM ani LIMIT 10</textarea>
                    <button class="btn-info" onclick="ejecutarSQL()">▶ EJECUTAR CONSULTA</button>
                </div>
                <div class="footer-note">
                    🌐 Conectado a base de datos en nube (Aiven) | Consultas en tiempo real
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Verificar conexión al cargar
        window.onload = function() { 
            verificarConexion(); 
        };
        
        function verificarConexion() {
            fetch('/api/verificar')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('connectionStatus');
                    if (data.connected) {
                        statusDiv.innerHTML = '<span>✅ Conectado a base de datos en nube (Aiven)</span>';
                        statusDiv.style.background = 'rgba(76, 175, 80, 0.2)';
                    } else {
                        statusDiv.innerHTML = '<span>❌ Error de conexión</span>';
                        statusDiv.style.background = 'rgba(244, 67, 54, 0.2)';
                    }
                })
                .catch(error => {
                    document.getElementById('connectionStatus').innerHTML = '<span>❌ Error de conexión</span>';
                });
        }
        
        function buscarPorCedula() {
            const cedula = document.getElementById('cedulaInput').value.trim();
            if (!cedula) {
                alert('Ingrese un número de cédula');
                return;
            }
            if (!/^\\d+$/.test(cedula)) {
                alert('La cédula debe contener solo números');
                return;
            }
            
            mostrarLoading();
            fetch('/api/buscar/cedula', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cedula: cedula })
            })
            .then(response => response.json())
            .then(data => mostrarResultados(data))
            .catch(error => mostrarError(error));
        }
        
        function buscarPorNombres() {
            const datos = {
                nombre1: document.getElementById('nombre1Input').value.trim(),
                nombre2: document.getElementById('nombre2Input').value.trim(),
                apellido1: document.getElementById('apellido1Input').value.trim(),
                apellido2: document.getElementById('apellido2Input').value.trim()
            };
            
            if (!datos.nombre1 && !datos.nombre2 && !datos.apellido1 && !datos.apellido2) {
                alert('Ingrese al menos un nombre o apellido');
                return;
            }
            
            mostrarLoading();
            fetch('/api/buscar/nombres', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            })
            .then(response => response.json())
            .then(data => mostrarResultados(data))
            .catch(error => mostrarError(error));
        }
        
        function verTodos() {
            mostrarLoading();
            fetch('/api/todos')
                .then(response => response.json())
                .then(data => mostrarResultados(data))
                .catch(error => mostrarError(error));
        }
        
        function ejecutarSQL() {
            const sql = document.getElementById('sqlQuery').value.trim();
            if (!sql) {
                alert('Escriba una consulta SQL');
                return;
            }
            
            mostrarLoading();
            fetch('/api/ejecutar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql: sql })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.message) {
                    mostrarMensaje(data.message);
                } else {
                    mostrarResultados(data);
                }
            })
            .catch(error => mostrarError(error));
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
            document.getElementById('connectionStatus').innerHTML = '<span>✅ Pantalla limpiada - Listo para nueva búsqueda</span>';
            setTimeout(() => verificarConexion(), 2000);
        }
        
        function mostrarLoading() {
            document.getElementById('resultsContainer').innerHTML = '<div class="loading"><div class="spinner"></div><p>Cargando datos...</p></div>';
        }
        
        function mostrarMensaje(mensaje) {
            document.getElementById('resultsContainer').innerHTML = '<div class="loading"><p class="success">✅ ' + mensaje + '</p></div>';
            document.getElementById('resultsCount').innerHTML = '<span class="success">✅ Operación completada</span>';
        }
        
        function mostrarResultados(data) {
            if (!data.success) {
                mostrarError(data.error || 'Error en la consulta');
                return;
            }
            
            if (!data.rows || data.rows.length === 0) {
                document.getElementById('resultsContainer').innerHTML = '<div class="loading"><p class="error">❌ No se encontraron registros</p></div>';
                document.getElementById('resultsCount').innerHTML = '<span class="error">0 registros encontrados</span>';
                return;
            }
            
            let html = '';
            data.rows.forEach((row, index) => {
                html += `
                    <div class="card">
                        <div class="card-header">📄 REGISTRO #${index + 1}</div>
                        <div class="card-body">
                `;
                
                for (const [key, value] of Object.entries(row)) {
                    let nombreCampo = formatearCampo(key);
                    let valorMostrar = (value === null || value === '') ? 'No especificado' : value;
                    html += `
                        <div class="info-row">
                            <div class="info-label">${nombreCampo}:</div>
                            <div class="info-value">${valorMostrar}</div>
                        </div>
                    `;
                }
                
                html += `</div></div>`;
            });
            
            document.getElementById('resultsContainer').innerHTML = html;
            document.getElementById('resultsCount').innerHTML = `<span class="success">✅ ${data.total} registro(s) encontrados | Fuente: NUBE (Aiven)</span>`;
        }
        
        function mostrarError(error) {
            document.getElementById('resultsContainer').innerHTML = `<div class="loading"><p class="error">❌ Error: ${error}</p></div>`;
            document.getElementById('resultsCount').innerHTML = '<span class="error">Error en la consulta</span>';
        }
        
        function formatearCampo(campo) {
            const nombres = {
                'ANINuip': '📇 NÚMERO DE CÉDULA',
                'ANINombre1': '👤 PRIMER NOMBRE',
                'ANINombre2': '👤 SEGUNDO NOMBRE',
                'ANIApellido1': '👥 PRIMER APELLIDO',
                'ANIApellido2': '👥 SEGUNDO APELLIDO',
                'LUGIdExpedicion': '📍 LUGAR DE EXPEDICIÓN',
                'LUGIdNacimiento': '🏠 LUGAR DE NACIMIENTO',
                'direccion': '🏡 DIRECCIÓN',
                'telefono': '📞 TELÉFONO',
                'email': '📧 CORREO ELECTRÓNICO',
                'fecha_nacimiento': '🎂 FECHA DE NACIMIENTO'
            };
            return nombres[campo] || campo.replace(/_/g, ' ').toUpperCase();
        }
    </script>
</body>
</html>
'''

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        if not DB_CONFIG['password']:
            print("Error: Contraseña no configurada")
            return None
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error de conexión: {e}")
        return None

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(HTML_COMPLETO)

@app.route('/api/verificar')
def verificar():
    """Verificar conexión a la base de datos"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'connected': True})
    return jsonify({'connected': False})

@app.route('/api/buscar/cedula', methods=['POST'])
def buscar_cedula():
    """Buscar por número de cédula"""
    data = request.json
    cedula = data.get('cedula', '').strip()
    
    if not cedula:
        return jsonify({'success': False, 'error': 'Cédula requerida'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión a la base de datos'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM ani WHERE ANINuip = %s"
        cursor.execute(query, (cedula,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'rows': rows, 'total': len(rows)})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/buscar/nombres', methods=['POST'])
def buscar_nombres():
    """Buscar por nombres y apellidos"""
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
        return jsonify({'success': False, 'error': 'Error de conexión a la base de datos'})
    
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
    """Ver todos los registros"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión a la base de datos'})
    
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
    """Ejecutar consulta SQL personalizada"""
    data = request.json
    sql = data.get('sql', '').strip()
    
    if not sql:
        return jsonify({'success': False, 'error': 'SQL requerido'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión a la base de datos'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        
        if cursor.description:  # Es SELECT
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'rows': rows, 'total': len(rows)})
        else:  # Es INSERT, UPDATE, DELETE
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': f'Consulta ejecutada correctamente. Filas afectadas: {affected}'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
