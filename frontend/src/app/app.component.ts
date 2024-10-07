import { Component, OnInit } from '@angular/core';
import { YoutubeService } from './services/youtube.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {

  constructor(private playlistService: YoutubeService) { }
  title = 'youtube-downloader';

  ngOnInit() {
    window.addEventListener('beforeunload', (event) => {
      if (this.playlistService.isDownloading()) {
        event.preventDefault();
        event.returnValue = ''; // Para alguns navegadores
      }
    });
  }
  
}
