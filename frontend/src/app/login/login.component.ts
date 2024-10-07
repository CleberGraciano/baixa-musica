import { Component } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';  // Importar Router

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  message: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  login() {
    this.authService.login(this.username, this.password).subscribe({
      next: (response) => {
        this.message = 'Login bem-sucedido!';
        localStorage.setItem('token', response.token);  // Armazenar token ou qualquer dado necessário
        this.router.navigate(['/app-download']);  // Redirecionar após login bem-sucedido
      },
      error: (error) => {
        console.error('Erro ao fazer login:', error);
        this.message = 'Erro ao fazer login: ' + error.error.message;
      }
    });
  }

  logout() {
    this.authService.performLogout();  // Chama o método para fazer logout
  }

  cadastrar(){
    this.router.navigate(['/register']);
  }
}
