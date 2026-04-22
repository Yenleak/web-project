import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';
import { Home } from './Components/home/home';
import { Login } from './Components/login/login';
import { Signup } from './Components/signup/signup';
import { Tasks } from './Components/tasks/tasks';
import { TaskDetail } from './Components/task-detail/task-detail';
import { WorkspaceComponent } from './Components/workspace/workspace';
import { WorkspaceDetail } from './Components/workspace-detail/workspace-detail';
import { Statistics } from './Components/statistics/statistics';
import { Search } from './Components/search/search';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'login', component: Login },
  { path: 'signup', component: Signup },
  { path: 'tasks', component: Tasks, canActivate: [authGuard] },
  { path: 'tasks/:id', component: TaskDetail, canActivate: [authGuard] },
  { path: 'workspaces', component: WorkspaceComponent, canActivate: [authGuard] },
  { path: 'workspaces/:id', component: WorkspaceDetail, canActivate: [authGuard] },
  { path: 'statistics', component: Statistics, canActivate: [authGuard] },
  { path: 'search', component: Search, canActivate: [authGuard] },
  { path: '**', redirectTo: '' }
];
