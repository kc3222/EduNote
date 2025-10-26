export async function login(email, password) {
    const res = await fetch(`/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // send/receive cookie
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    return res.json();
  }
  
  export async function me() {
    const res = await fetch(`/auth/me`, { credentials: "include" });
    return res.json();
  }
  
  export async function logout() {
    const res = await fetch(`/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    return res.json();
  }

export async function createNote(noteData) {
  const res = await fetch(`/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(noteData),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to create note");
  }
  return res.json();
}

export async function updateNote(noteId, noteData) {
  console.log("Updating note:", noteId, noteData);
  const res = await fetch(`/notes/${noteId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(noteData),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to update note");
  }
  return res.json();
}

export async function getNote(noteId) {
  const res = await fetch(`/notes/${noteId}`);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to get note");
  }
  return res.json();
}

export async function getUserNotes(ownerId) {
  const res = await fetch(`/notes?owner_id=${ownerId}`);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to get user notes");
  }
  return res.json();
}

// Document API functions
export async function uploadDocument(formData) {
  const res = await fetch(`/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to upload document");
  }
  return res.json();
}

export async function getUserDocuments(ownerId) {
  const res = await fetch(`/documents?owner_id=${ownerId}`);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to get user documents");
  }
  return res.json();
}

export async function getDocument(documentId) {
  const res = await fetch(`/documents/${documentId}`);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to get document");
  }
  return res.json();
}

export async function deleteDocument(documentId) {
  const res = await fetch(`/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to delete document");
  }
  return res.json();
}
  