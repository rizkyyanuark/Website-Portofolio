// filepath: /C:/Users/rizky/OneDrive/Dokumen/GitHub/Website-Portofolio/dist/js/chat.js
export default async function handler(req, res) {
  if (req.method === "POST") {
    try {
      const { message } = req.body;

      const apiUrl = process.env.API_URL; // Mengambil environment variable

      const apiResponse = await fetch(`${apiUrl}/chatbot`, {
        method: "POST",
        body: JSON.stringify({ message }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await apiResponse.json();
      res.status(200).json(data); // Mengirimkan hasil ke frontend
    } catch (error) {
      res.status(500).json({ error: "Error processing request" });
    }
  } else {
    res.status(405).json({ error: "Method Not Allowed" });
  }
}
