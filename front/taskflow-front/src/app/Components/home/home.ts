import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../Services/auth';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home {
  constructor(public auth: AuthService, private router: Router) {}

  goToTasks() {
    this.router.navigate(['/tasks']);
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }

  logout() {
    this.auth.logout();
  }
}
