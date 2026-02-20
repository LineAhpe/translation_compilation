
// Тестовая программа


#include <iostream>
#include <windows.h>
using namespace std; // чтоб std не писать

// математическая функция сложения


int summ(int a, int    b) {
    return a + b;
}

// математическая функция умножения
int mult(int a, int b) {
    return a * b;
}

// Математическая функция разности
int diff(int a, int b) {
    if (a > b) {
        return a - b;
    }
    return b - a;
}

/* Основная программа
* Просит ввести числа a и b */
* Затем просит выбрать дейтвие с этими числами
*/
int main() {
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    int a, b;
    bool fl = true;

    while (fl) {
        cout << "Введите число a: ";
        cin >> a;

        cout << "Введите число b: ";
        cin >> b;

        cout << "Выберите действие: " << endl;
        cout << "1 - сложение (a + b)" << endl;
        cout << "2 - умножение (a * b)" << endl;
        cout << "3 - разность |a - b|" << endl;
        cout << "0 - выход" << endl;

        int choice;
        cout << "Ваш выбор: ";
        cin >> choice;

        switch (choice) {
        case 1:
            cout << "Сумма: " << summ(a, b) << endl;
            break;
        case 2:
            cout << "Умножение: " << mult(a, b) << endl;

            break;
        case 3:
            cout << "Разность: " << diff(a, b) << endl;
            break;

        case 0:
            fl = false;
            break;

        default:
            cout << "Ошибка: неверный пункт меню." << endl;
            break;
        }
    }
    return 0;
}