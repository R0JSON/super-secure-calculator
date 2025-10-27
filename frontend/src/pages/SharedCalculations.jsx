import React, { useEffect, useState } from "react";

function SharedCalculations({ token }) {
  const [shared, setShared] = useState([]);

  useEffect(() => {
    fetch("http://localhost:3001/api/v1/share/", {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Otrzymane dane:", data);
        setShared(data);
      })
      .catch((err) => console.error("Błąd fetch:", err));
  }, [token]);

  if (!shared.length) {
    return <p>Brak udostępnionych obliczeń.</p>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Udostępnione obliczenia</h2>

      {/* Karty / schemat posta */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "20px" }}>
        {shared.map((item) => (
          <div
            key={item.id}
            style={{
              border: "1px solid #ccc",
              borderRadius: "8px",
              padding: "15px",
              width: "250px",
              boxShadow: "2px 2px 8px rgba(0,0,0,0.1)",
              backgroundColor: "#f9f9f9",
            }}
          >
            <h4 style={{ margin: "0 0 10px 0" }}>{item.expression}</h4>
            <p style={{ margin: "0 0 5px 0" }}>
              <b>Wynik:</b> {item.result}
            </p>
            <p style={{ margin: "0", fontSize: "12px", color: "#555" }}>
              Utworzono: {item.created_at ? new Date(item.created_at).toLocaleString() : "-"}
            </p>
            <p style={{ margin: "0", fontSize: "12px", color: "#777" }}>
              Użytkownik: {item.user_id ?? "-"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SharedCalculations;

