import { Component, OnInit } from '@angular/core';
import { PlaylistService } from '../services/playlist.service';

@Component({
  selector: 'app-playlists',
  templateUrl: './playlists.component.html',
  styleUrl: './playlists.component.css'
})
export class PlaylistsComponent implements OnInit {
  playlists: any[] = [];
  newPlaylistName: string = '';
  message: string = '';

  constructor(private playlistService: PlaylistService) {}

  ngOnInit(): void {
    this.loadPlaylists();
  }

  loadPlaylists() {
    this.playlistService.getPlaylists().subscribe({
      next: (response) => {
        this.playlists = response.playlists;
      },
      error: (error) => {
        this.message = 'Erro ao carregar playlists!';
      }
    });
  }

  createPlaylist() {
    this.playlistService.createPlaylist(this.newPlaylistName).subscribe({
      next: (response) => {
        this.message = response.message;
        this.newPlaylistName = ''; // Limpa o campo de entrada
        this.loadPlaylists(); // Recarrega a lista de playlists
      },
      error: (error) => {
        this.message = 'Erro ao criar a playlist!';
      }
    });
  }
}

