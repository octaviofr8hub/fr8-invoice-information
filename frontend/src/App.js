

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
      const res = await fetch('http://localhost:8005/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (res.ok && data.status === 'received') {
        setResponse(data);
        setStatus('Extraccion realizada con exito ✅');
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

  const downloadCSV = () => {
    if (!response || !response.resultado) return;

    const headers = ['Campo', 'Valor', 'Error'];

    const rows = Object.entries(response.resultado).map(([key, value]) => [
      key.replace('pdf_', '').replace('_', ' '),
      value.toString(),
      /*response.errores[key] ? '❌' : '✅'*/
      response.errores[key] ? 'True' : 'False'
    ]);

    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `factura_${file?.name || 'resultado'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadJSON = () => {
    if (!response) return;
    const jsonContent = JSON.stringify({
      status: response.status,
      resultado: response.resultado,
      errores: response.errores
    }, null, 2);

    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `factura_${file?.name || 'resultado'}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container">
      <h1>Subir Factura PDF</h1>
      <input type="file" accept="application/pdf" onChange={handleFileChange} disabled={isLoading}/>
      {file && <p>Archivo seleccionado: {file.name}</p>}
      <button onClick={handleUpload} disabled={isLoading}>
        Extraer informacion
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
          <h3>Informacion extraida:</h3>
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
          <div className="download-buttons">
            <button onClick={downloadCSV} disabled={isLoading}>
              Descargar como CSV
            </button>
            <button onClick={downloadJSON} disabled={isLoading}>
              Descargar como JSON
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
