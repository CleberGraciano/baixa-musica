import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:5000'; // URL da sua API

  constructor(private http: HttpClient, private router: Router) {}

  register(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, { username, password });
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { username, password }, { withCredentials: true });
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/logout`, {}, { withCredentials: true });
  }
  // Método para realizar o logout e redirecionar o usuário
  performLogout() {
    this.logout().subscribe(
      response => {
        console.log('Logout bem-sucedido!', response);
        this.router.navigate(['/login']);  // Redireciona para a página de login
      },
      error => {
        console.error('Erro ao fazer logout:', error);
      }
    );
  }
}
