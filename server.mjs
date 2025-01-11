// filepath: /C:/Users/rizky/OneDrive/Dokumen/GitHub/Website-Portofolio/server.mjs
import dotenv from "dotenv";
import express from "express";
import fetch from "node-fetch";

dotenv.config();
const app = express();
const port = 3000;

app.use(express.json());

app.post("/js/chat", async (req, res) => {
  const { message } = req.body;
  try {
    const response = await fetch(`${process.env.API_URL}/chatbot`, {
      method: "POST",
      body: JSON.stringify({ message }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
