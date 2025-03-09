import { PageFilter } from "@/components/ui/pageFilter";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

vi.mock("@/services/services", () => ({
  getGames: vi.fn(),
}));

const setIsFilteringMock = vi.fn();
const setFormDataMock = vi.fn();
const fetchGamesMock = vi.fn();

const mockedData = {
  total_pages: 1,
  games: [
    {
      id: 1,
      players_count: "4",
      max_players: 4,
      min_players: 2,
      name: "testName1",
      is_private: false,
    },
    {
      id: 2,
      players_count: "4",
      max_players: 4,
      min_players: 2,
      name: "testName2",
      is_private: false,
    },
  ],
};

describe("PageFilter Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchGamesMock.mockResolvedValue(mockedData); 
  });

  // Test para verificar que se renderiza el componente de filtro, abre y cierra el Popover al hacer clic
  it("renders filter component, opens and closes Popover on click", async () => {
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: "", players: "" }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );

    const triggerButton = screen.getByTestId("triggerButton");
    expect(triggerButton).toBeInTheDocument();
    fireEvent.click(triggerButton);

    const popOver = await screen.findByTestId("popOverId");
    expect(popOver).toBeInTheDocument();

    const submitButton = screen.getByTestId("submitButtonId");
    expect(submitButton).toBeInTheDocument();

    fireEvent.click(submitButton);
    await waitFor(() => {
      expect(screen.queryByTestId("popOverId")).not.toBeInTheDocument();
    });
  });

  // Test para verificar que se actualiza formData en el cambio de entrada
  it("updates formData on input change", () => {
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: "", players: "" }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );

    fireEvent.click(screen.getByTestId("triggerButton"));

    const nameInput = screen.getByLabelText("Nombre");
    fireEvent.change(nameInput, { target: { value: "Test Game" } });
    expect(setFormDataMock).toHaveBeenCalledWith({ name: "Test Game", players: "" });
  });
      
  // Test para verificar que se manejan los errores en fetchGames
  it('handles errors in fetchGames gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    fetchGamesMock.mockRejectedValue(new Error('Network error'));
  
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: 'Test Game', players: '4' }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );
  
    // Abrir el popover y enviar el formulario
    fireEvent.click(screen.getByTestId('triggerButton'));
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Test Game' } });
    fireEvent.change(screen.getByLabelText('N° jugadores'), { target: { value: '4' } });
    fireEvent.click(screen.getByTestId('submitButtonId'));
  
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error occurred while filtering');
      expect(setIsFilteringMock).toHaveBeenCalledWith(false);
    });
  
    consoleSpy.mockRestore();
  });

  // Test para verificar que se filtran los juegos correctamente
  it('filters games correctly', async () => {
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: 'Test Game', players: '4' }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );
  
    // Abrir el popover y enviar el formulario
    fireEvent.click(screen.getByTestId('triggerButton'));
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Test Game' } });
    fireEvent.change(screen.getByLabelText('N° jugadores'), { target: { value: '4' } });
    fireEvent.click(screen.getByTestId('submitButtonId'));
  
    await waitFor(() => {
      expect(fetchGamesMock).toHaveBeenCalledWith(1, { name: 'Test Game', players: '4' });
    });
  });

  // Test para verificar que no se filtran los juegos si no hay datos
  it('does not filter games if no data is provided', async () => {
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: '', players: '' }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );
  
    // Abrir el popover y enviar el formulario
    fireEvent.click(screen.getByTestId('triggerButton'));
    fireEvent.click(screen.getByTestId('submitButtonId'));
  
    await waitFor(() => {
      expect(fetchGamesMock).not.toHaveBeenCalled();
    });
  });

  // Test para verificar que se actualiza el estado de setIsFiltering correctamente
  it('updates setIsFiltering state correctly', async () => {
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: '', players: '' }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );
  
    // Abrir el popover y enviar el formulario
    fireEvent.click(screen.getByTestId('triggerButton'));
    fireEvent.click(screen.getByTestId('submitButtonId'));
  
    await waitFor(() => {
      expect(setIsFilteringMock).toHaveBeenCalledWith(true);
    });
  });

  // Test para verificar que se cierra el Popover después de enviar el formulario
  it('closes Popover after submitting form', async () => {
    render(
      <PageFilter
        setIsFiltering={setIsFilteringMock}
        formData={{ name: '', players: '' }}
        setFormData={setFormDataMock}
        fetchGames={fetchGamesMock}
      />
    );
  
    // Abrir el popover y enviar el formulario
    fireEvent.click(screen.getByTestId('triggerButton'));
    fireEvent.click(screen.getByTestId('submitButtonId'));
  
    await waitFor(() => {
      expect(screen.queryByTestId('popOverId')).not.toBeInTheDocument();
    });
  });
});
