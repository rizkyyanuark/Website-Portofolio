const fetch = require("node-fetch");

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ message: "No message provided" });
  }

  try {
    const response = await fetch(process.env.API_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.API_KEY}`, // Use environment variable for API key
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error("Error:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
};
