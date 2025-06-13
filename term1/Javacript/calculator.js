function calculate(op) {
    const n1 = parseFloat(document.getElementById('num1').value);
    const n2 = parseFloat(document.getElementById('num2').value);
    let result = '';

    if (isNaN(n1) || isNaN(n2)) {
      result = 'กรุณากรอกตัวเลขทั้งสองช่อง';
    } else {
      switch(op) {
        case '+': result = n1 + n2; break;
        case '-': result = n1 - n2; break;
        case '*': result = n1 * n2; break;
        case '/': 
          result = n2 !== 0 ? (n1 / n2) : 'หารด้วยศูนย์ไม่ได้';
          break;
      }
    }

    document.getElementById('result').textContent = 'ผลลัพธ์: ' + result;
  }