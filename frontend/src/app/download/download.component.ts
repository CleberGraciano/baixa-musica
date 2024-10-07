import { Component, OnInit, OnDestroy } from '@angular/core';
import { YoutubeService } from '../services/youtube.service';

@Component({
  selector: 'app-download',
  templateUrl: './download.component.html',
  styleUrls: ['./download.component.css']
})
export class DownloadComponent implements OnInit {
  videoLink: string = '';
  downloadInProgress: boolean = false;
  threadId: string = '';
  errorMessage: string = '';
  mp3Files: string[] = [];
  intervalId: any;  // Para armazenar o ID do intervalo
  

  constructor(private playlistService: YoutubeService) { }

  ngOnInit(): void {
    this.loadMp3Files();
    this.intervalId = setInterval(() => {
      this.loadMp3Files(); // Atualiza a lista a cada 5 segundos
    }, 10000); // 5000 milissegundos = 10 segundos

    // this.socketService.listenToDownloadComplete((data) => {
    //   this.mp3Files.push(data.filename); // Adiciona o arquivo baixado à lista
    //   alert(`Download concluído: ${data.filename}`); // Alerta o usuário (ou você pode atualizar a interface de outra maneira)
    // });

  }

  ngOnDestroy(): void {
    clearInterval(this.intervalId); // Limpa o intervalo ao destruir o componente
  }

  downloadVideo() {
    if (!this.videoLink) {
      this.errorMessage = 'Por favor, insira um link.';
      return;
    }
  
    this.downloadInProgress = true;
    this.playlistService.setDownloading(true)
  
    this.playlistService.downloadVideo(this.videoLink).subscribe({
      next: (response) => {
        this.threadId = response.thread_id;  // Armazena o thread_id (hash MD5)
        this.downloadInProgress = true;
        this.playlistService.setDownloading(true)
      },
      error: (error) => {
        this.errorMessage = 'Erro ao iniciar o download.';
        this.downloadInProgress = false;
        this.playlistService.setDownloading(false)
      }
    });
  }
  
  cancelDownload() {
    if (this.threadId) {
      this.playlistService.cancelDownload(this.threadId).subscribe({
        next: () => {
          this.downloadInProgress = false;
          this.playlistService.setDownloading(false)
        },
        error: () => {
          this.errorMessage = 'Erro ao cancelar o download.';
         
        }
      });
    }
  }

   // Método para carregar a lista de arquivos MP3
   loadMp3Files(): void {
    this.playlistService.getMp3Files().subscribe({
      next: (response) => {
        this.mp3Files = response.files;
      },
      error: (error) => {
        this.errorMessage = 'Erro ao carregar os arquivos MP3';
      }
    });
  }

  // Método para baixar o arquivo MP3
  downloadFile(filename: string): void {
    const link = document.createElement('a');
    link.href = `http://localhost:5000/download/${filename}`; // URL para download
    link.download = filename; // Define o nome do arquivo a ser baixado
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}