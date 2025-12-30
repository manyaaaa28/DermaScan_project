function showPage(pageId) {
      document.getElementById('home').style.display = pageId === 'home' ? 'block' : 'none';
      document.getElementById('dashboard').classList.toggle('active', pageId === 'dashboard');
    }
    showPage('home');


  window.onload = function() {
    setTimeout(() => {
      document.getElementById('splash-screen').style.opacity = '0';
      setTimeout(() => {
        document.getElementById('splash-screen').style.display = 'none';
      }, 1000); // Wait for fade-out to finish
    }, 3000); // Show splash for 3 seconds
  };

  


  const text = "DermaScan";
  let index = 0;

  function typeWriter() {
    if (index < text.length) {
      document.getElementById("typewriter").innerHTML += text.charAt(index);
      index++;
      setTimeout(typeWriter, 150);
    }
  }

window.onload = function() {
    runTypewriter();
    
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => { 
                splash.style.display = 'none'; 
            }, 1000);
        }
    }, 3000);
};



function handleAnalyze(event) {
  event.preventDefault(); // Prevent form refresh

  // Simulated AI result
  const result = `Detected: Mild Acne
Confidence: 85%
Advice: Use a gentle cleanser and consult a dermatologist if needed.`;

  document.getElementById("resultText").innerText = result;
}




document.addEventListener("DOMContentLoaded", () => {
  // 📸 Image Preview Logic
  const fileInput = document.getElementById("imageInput");
  const preview = document.getElementById("previewImage");

  if (fileInput && preview) {
    fileInput.addEventListener("change", function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          preview.setAttribute("src", e.target.result);
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // 💬 DermaGPT Chat Logic
  const sendBtn = document.getElementById("sendBtn");
  const userInput = document.getElementById("userInput");
  const responseBox = document.getElementById("chatResponse");

  if (sendBtn && userInput && responseBox) {
    sendBtn.addEventListener("click", async () => {
      const input = userInput.value.trim();
      if (!input) return;

      responseBox.innerHTML = "⏳ Thinking...";

      try {
        const res = await fetch("", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    
  },
  body: JSON.stringify({
    model: "gpt-3.5-turbo",
    messages: [{ role: "user", content: input }],
    temperature: 0.7,
    max_tokens: 150
  })
});


        const data = await res.json();
        const reply = data.choices?.[0]?.message?.content || "No reply received.";
        responseBox.innerHTML = `<strong>🧠 DermaGPT:</strong> ${reply}`;
      } catch (error) {
        console.error("Error:", error);
        responseBox.innerHTML = `<strong>❌ Error:</strong> ${error.message}`;
      }
    });
  }
});
function answerQuestion() {
  const question = document.getElementById('user-question').value.toLowerCase();
  const answerBox = document.getElementById('ai-answer');

  if (question.includes("acne")) {
    answerBox.innerText = "Try using a salicylic acid-based cleanser and avoid oily products.";
  } 
  else if (question.includes("allergy")) {
    answerBox.innerText = "Apply a cold compress and consult a dermatologist if the allergy worsens.";
  }
  else if (question.includes("rash")) {
    answerBox.innerText = "Keep the area clean and dry. Use a mild hydrocortisone cream if needed.";
  }
  else {
    answerBox.innerText = "I'm sorry, I don't have an answer for that yet. Please try asking about acne, allergy, or rash.";
  }
}
