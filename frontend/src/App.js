

import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type === 'application/pdf') {
      setFile(selected);
      setStatus('');
      setResponse(null);
    } else {
      setStatus('Por favor selecciona un archivo PDF válido.');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Primero selecciona un archivo.');
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setIsLoading(true);
      setStatus('Procesando archivo...');
      const res = await fetch('http://localhost:8000/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (res.ok && data.status === 'received') {
        setResponse(data);
        setStatus('Respuesta recibida del agente ✅');
      } else {
        setStatus(`Error: ${data.message || 'desconocido'}`);
      }
    } catch (err) {
      console.error(err);
      setStatus('Ocurrió un error al procesar el archivo ❌');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Subir Factura PDF</h1>
      <input type="file" accept="application/pdf" onChange={handleFileChange} disabled={isLoading}/>
      {file && <p>Archivo seleccionado: {file.name}</p>}
      <button onClick={handleUpload} disabled={isLoading}>
        Enviar al agente
      </button>
      <p className="status">{status}</p>
      {isLoading && (
        <div className="spinner">
          <div className="loader"></div>
          <p>Procesando...</p>
        </div>
      )}
      {response && response.resultado && (
        <div className="response">
          <h3>Resultado:</h3>
          <table>
            <thead>
              <tr>
                <th>Campo</th>
                <th>Valor</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(response.resultado).map(([key, value]) => (
                <tr key={key}>
                  <td>{key.replace('pdf_', '').replace('_', ' ')}</td>
                  <td>{value.toString()}</td>
                  <td>{response.errores[key] ? '❌' : '✅'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
