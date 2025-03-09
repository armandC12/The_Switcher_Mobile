import {render, screen} from "@testing-library/react"
import GamesList from "@/components/ui/GamesList";
import { MemoryRouter } from "react-router-dom"; 

describe('Listado de partidas', ()=> {
    it('Deberia mostrar "No hay partidas creadas aun" cuando llega un arreglo vacio y loading esta en false', ()=> {
        render(<MemoryRouter><GamesList games={[]}  setCurrentPage={1} totalPages={1} loading={false}/></MemoryRouter>);
        const noGamesMsg = screen.getByText(/No hay partidas creadas aun./i);
        expect(noGamesMsg).toBeInTheDocument();
    })

    it('Deberia mostrar "Loading..." cuando llega un arreglo vacio y loading esta en true', ()=> {
        render(<MemoryRouter><GamesList games={[]}  setCurrentPage={1} totalPages={1} loading={true}/></MemoryRouter>);
        const noGamesMsg = screen.getByText(/Loading/i);
        expect(noGamesMsg).toBeInTheDocument();
    })

    it('Deberia mostrar el listado cuando llega un arreglo no vacio', ()=> {
        const mockGames = [
            {
              id: 1,
              name: "Partida de Aventura",
              currentPlayers: 3,
              maxPlayers: 5,
              isPrivate: false,
            },
            {
              id: 2,
              name: "Partida de Estrategia",
              currentPlayers: 4,
              maxPlayers: 4,
              isPrivate: true,
            },
            {
              id: 3,
              name: "Partida de Acción",
              currentPlayers: 2,
              maxPlayers: 8,
              isPrivate: false,
            }
          ];
          
        render(<MemoryRouter><GamesList games={mockGames} currentPage="" setCurrentPage="" totalPages="" loading=""/></MemoryRouter>);
        
        const listItems = screen.getAllByRole('listitem');
        expect(listItems.length).toBe(mockGames.length);
    })
});