import { Component } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  username: string = '';
  password: string = '';
  message: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  register() {
    this.authService.register(this.username, this.password).subscribe({
      next: (response) => {
        this.message = 'Registro bem-sucedido! Você pode fazer login agora.';
        this.username = '';
        this.password = '';
      },
      error: (error) => {
        this.message = 'Erro ao registrar: ' + error.error.message;
      }
    });
  }

  voltar(){
    this.router.navigate(['/login']);
  }
}
