import { useState } from "react";
import axios from "axios";

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setResponse(res.data);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  return (
    <div className="p-4 border rounded-lg">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>
        Upload Resume
      </button>

      {response && (
        <pre>{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}