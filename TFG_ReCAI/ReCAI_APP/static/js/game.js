function generateWords() {
    document.getElementById('word1').textContent = "Palabra 1: " + "Payaso";
    document.getElementById('word2').textContent = "Palabra 2: " + "Camión";
    document.getElementById('letter').textContent = "Letra: " + "B";
}

function checkSolution() {
var solution = document.getElementById('solution').value.trim();

if (solution.toLowerCase() === "Bombero".toLowerCase()) {
    document.getElementById('result').textContent = "¡Correcto!";
} else {
    document.getElementById('result').textContent = "Incorrecto. Intenta de nuevo.";
}
}