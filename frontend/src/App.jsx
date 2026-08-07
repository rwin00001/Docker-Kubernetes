import React, { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "";

export default function App() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [saved, setSaved] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("search");
  const [selectedImage, setSelectedImage] = useState(null);
  const [showModal, setShowModal] = useState(false);

  async function doSearch(e) {
    e?.preventDefault();
    if (!q.trim()) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(q)}&per_page=20`);
      const j = await res.json();
      setResults(j.results || []);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function doSave(item) {
    try {
      const payload = {
        ...item
      };
      
      await fetch(`${API_BASE}/api/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      // Refresh saved images
      loadSaved();
    } catch (error) {
      console.error("Save error:", error);
    }
  }

  async function deleteImage(imageId) {
    if (!window.confirm("Are you sure you want to delete this image?")) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/saved/${imageId}`, {
        method: "DELETE",
      });
      
      if (response.ok) {
        // Remove from local state
        setSaved(saved.filter(img => img.id !== imageId));
      } else {
        console.error("Failed to delete image");
      }
    } catch (error) {
      console.error("Delete error:", error);
    }
  }

  async function loadSaved() {
    try {
      const r = await fetch(`${API_BASE}/api/saved`);
      const j = await r.json();
      setSaved(j.items || []);
    } catch (error) {
      console.error("Load saved error:", error);
    }
  }

  function downloadImage(url, filename) {
    fetch(url)
      .then(response => response.blob())
      .then(blob => {
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = filename || 'image.jpg';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(blobUrl);
        document.body.removeChild(a);
      })
      .catch(() => {
        // Fallback to opening in new tab if download fails
        window.open(url, '_blank');
      });
  }

  function shareImage(url) {
    if (navigator.share) {
      navigator.share({
        title: 'Check out this image',
        url: url
      })
      .catch(console.error);
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(url)
        .then(() => alert('Link copied to clipboard!'))
        .catch(() => {
          // Final fallback: prompt
          prompt('Copy this link:', url);
        });
    }
  }

  function openImageModal(image) {
    setSelectedImage(image);
    setShowModal(true);
  }

  function closeImageModal() {
    setShowModal(false);
    setSelectedImage(null);
  }

  useEffect(() => {
    loadSaved();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📷 Image Gallery</h1>
        <p>Discover and save beautiful images</p>
      </header>

      <div className="tabs">
        <button 
          className={activeTab === "search" ? "tab active" : "tab"}
          onClick={() => setActiveTab("search")}
        >
          <i className="fas fa-search"></i> Search
        </button>
        <button 
          className={activeTab === "saved" ? "tab active" : "tab"}
          onClick={() => setActiveTab("saved")}
        >
          <i className="fas fa-bookmark"></i> Saved ({saved.length})
        </button>
      </div>

      {activeTab === "search" && (
        <div className="search-section">
          <form onSubmit={doSearch} className="search-form">
            <div className="search-input-container">
              <i className="fas fa-search search-icon"></i>
              <input 
                value={q} 
                onChange={(e) => setQ(e.target.value)} 
                placeholder="Search for images..." 
                className="search-input"
              />
              <button type="submit" className="search-button" disabled={loading}>
                {loading ? <i className="fas fa-spinner fa-spin"></i> : "Search"}
              </button>
            </div>
          </form>

          {loading && <div className="loading"><i className="fas fa-spinner fa-spin"></i> Searching...</div>}

          <div className="results-grid">
            {results.map(r => (
              <div key={r.unsplash_id} className="image-card">
                <img 
                  src={r.thumb} 
                  alt={r.alt} 
                  className="image-thumb"
                  onClick={() => openImageModal(r)}
                />
                <div className="image-actions">
                  <button onClick={() => doSave(r)} className="save-btn" title="Save image">
                    <i className="fas fa-bookmark"></i>
                  </button>
                  <button onClick={() => downloadImage(r.full)} className="download-btn" title="Download">
                    <i className="fas fa-download"></i>
                  </button>
                  <button onClick={() => shareImage(r.full)} className="share-btn" title="Share">
                    <i className="fas fa-share-alt"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {results.length === 0 && !loading && q && (
            <div className="no-results">
              <i className="fas fa-search"></i>
              <p>No results found for "{q}"</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "saved" && (
        <div className="saved-section">
          {saved.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-inbox"></i>
              <h3>No saved images yet</h3>
              <p>Search for images and save your favorites!</p>
            </div>
          ) : (
            <div className="saved-grid">
              {saved.map(s => (
                <div key={s.id} className="saved-image-card">
                  <img 
                    src={s.thumb} 
                    alt={s.alt} 
                    className="saved-image"
                    onClick={() => openImageModal(s)}
                  />
                  <button 
                    onClick={() => deleteImage(s.id)} 
                    className="delete-btn"
                    title="Delete image"
                  >
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {showModal && selectedImage && (
        <div className="modal-overlay" onClick={closeImageModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={closeImageModal}>
              <i className="fas fa-times"></i>
            </button>
            <img src={selectedImage.full} alt={selectedImage.alt} className="modal-image" />
            <div className="modal-actions">
              <button onClick={() => downloadImage(selectedImage.full)} className="modal-btn">
                <i className="fas fa-download"></i> Download
              </button>
              <button onClick={() => shareImage(selectedImage.full)} className="modal-btn">
                <i className="fas fa-share-alt"></i> Share
              </button>
              <button onClick={() => doSave(selectedImage)} className="modal-btn">
                <i className="fas fa-bookmark"></i> Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
