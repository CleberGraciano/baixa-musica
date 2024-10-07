import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PlaylistService {
  private apiUrl = 'http://localhost:5000'; // URL da sua API

  constructor(private http: HttpClient) { }

  createPlaylist(name: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/playlists`, { name });
  }

  getPlaylists(): Observable<any> {
    return this.http.get(`${this.apiUrl}/playlists`);
  }
}
