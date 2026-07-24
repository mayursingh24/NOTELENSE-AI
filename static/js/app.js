// ================= NOTE LENSE APP JS =================

const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileUpload");
const resultContainer = document.getElementById("result-container");

function renderMessage(title, message) {

    resultContainer.innerHTML = `

        <div class="result-card">

            <h3>${title}</h3>

            <p>${message}</p>

        </div>

    `;

}

uploadForm.addEventListener("submit", async function(e){

    e.preventDefault();

    if(fileInput.files.length===0){

        alert("Please select a file.");

        return;

    }

    resultContainer.innerHTML=`

        <div class="result-card">

            <div class="loader"></div>

            <h3>

                🤖 Gemini AI is analyzing...

            </h3>

            <p>

                Creating Summary, Notes,
                MCQs and Study Guide...

            </p>

        </div>

    `;

    const formData=new FormData();

    formData.append("notes",fileInput.files[0]);

    try{

        const response=await fetch("/analyze",{

            method:"POST",

            body:formData

        });

        const data=await response.json();

        if(data.error){

            renderMessage("❌ Error",data.error);

            return;

        }

        let html="";

        if(typeof marked!=="undefined"){

            html=marked.parse(data.result);

        }

        else{

            html=data.result.replace(/\n/g,"<br>");

        }

        resultContainer.innerHTML=`

            <div class="result-card">

                <img

                src="/static/images/logo.png"

                class="result-logo">

                <h2>

                    📘 AI Study Guide

                </h2>

                ${
                    data.warning ?

                    `<div class="ai-warning">

                        <strong>${data.warning}</strong>

                        <br>

                        ${data.warning_detail || ""}

                    </div>`

                    :

                    ""

                }

                <div class="ai-result">

                    ${html}

                </div>

            </div>

        `;

        if(typeof renderMathInElement==="function"){

            renderMathInElement(

                document.querySelector(".ai-result"),

                {

                    delimiters:[

                        {

                            left:"$$",

                            right:"$$",

                            display:true

                        },

                        {

                            left:"$",

                            right:"$",

                            display:false

                        }

                    ]

                }

            );

        }

        window.location.href="#dashboard";

    }

    catch(error){

        console.log(error);

        renderMessage(

            "❌ Server Error",

            "Unable to connect with backend."

        );

    }

});