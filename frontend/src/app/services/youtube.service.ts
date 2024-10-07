import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class YoutubeService {

  private API_URL = 'http://localhost:5000';

  private downloading: boolean = false;

  constructor(private http: HttpClient) { }

  downloadVideo(link: string): Observable<any> {
    return this.http.post(`${this.API_URL}/download`, { link }, { withCredentials: true });
  }

  cancelDownload(threadId: string): Observable<any> {
    return this.http.post(`${this.API_URL}/cancel/${threadId}`, {}, { withCredentials: true });
  }

  // Método para obter a lista de arquivos MP3
  getMp3Files(): Observable<any> {
    return this.http.get(`${this.API_URL}/list-mp3`, { withCredentials: true });
  }


  setDownloading(value: boolean) {
    this.downloading = value;
  }

  isDownloading(): boolean {
    return this.downloading;
  }
}
