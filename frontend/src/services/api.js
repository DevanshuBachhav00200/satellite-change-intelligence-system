const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function fetchHealthStatus() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Health check error:", err);
    return { status: 'unhealthy', model_loaded: false, error: err.message };
  }
}

export async function fetchSamplesList() {
  try {
    const res = await fetch(`${API_BASE}/samples`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data.samples || [];
  } catch (err) {
    console.error("Fetch samples error:", err);
    return [];
  }
}

export async function analyzeImagePair(fileA, fileB) {
  const formData = new FormData();
  formData.append('image_a', fileA);
  formData.append('image_b', fileB);

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis engine failed to process images.' }));
    throw new Error(errorData.detail || 'Image analysis failed.');
  }

  return await res.json();
}

export async function analyzeSamplePair(sampleName) {
  const res = await fetch(`${API_BASE}/analyze-sample`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ sample_name: sampleName }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Sample analysis failed.' }));
    throw new Error(errorData.detail || 'Sample analysis failed.');
  }

  return await res.json();
}
