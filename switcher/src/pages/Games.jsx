import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaPlus, FaPlay } from 'react-icons/fa';
import GamesList from '../components/ui/GamesList';
import { useGameSocket } from '../components/hooks/use-games-socket';
import { getGames, joinGame } from '../services/services';
import { useGameContext } from '@/context/GameContext';
import { PageFilter } from '@/components/ui/pageFilter';
import { MdOutlineCleaningServices } from "react-icons/md";

const PasswordModal = ({ isOpen, onClose, onSubmit, error }) => {
  const [password, setPassword] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(password);
    setPassword('');
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-zinc-900 p-8 rounded-lg shadow-md border border-zinc-800 w-80 h-auto mx-auto">
        <h2 className="text-3xl mb-4">Ingrese la contraseña</h2>
        <form onSubmit={handleSubmit}>

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full bg-zinc-800 text-white rounded-full px-4 py-2 focus:outline-none"
          />
          {error && <p className="text-red-500 mt-1 ml-2">Contraseña incorrecta</p>}
          <div className="flex mt-6 justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-400 hover:bg-gray-300 rounded"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded"
            >
              Entrar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Games = () => {
  const navigate = useNavigate();
  const [games, setGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(10);
  const [loading, setLoading] = useState(true);
  const { setPlayerId, username } = useGameContext();
  const [formData, setFormData] = useState({ name: '', players: '' });
  const [isFiltering, setIsFiltering] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [error, setError] = useState('');


  const handleCreateGame = () => {
    navigate('/games/create');
  };

  const handleRemoveFilter = async () => {
    setIsFiltering(false);
    fetchGames(currentPage, {});
  };

  const fetchGames = async (page, formData) => {
    try {
      const data = await getGames(page, formData, isFiltering);
      setGames(data.games);
      setTotalPages(data.total_pages);
    } catch (error) {
      console.error("Couldn't fetch games");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGame = () => {
    if (selectedGame) {
      if (selectedGame.is_private) {
        // Open modal if game is private
        setIsPasswordModalOpen(true);
      } else {
        // Join directly if game is public
        joinGame(selectedGame.id, username)
          .then((res) => {
            setPlayerId(res.player_id);
            navigate(`/games/lobby/${selectedGame.id}/${res.player_id}`);
          })
          .catch((err) => console.error("Error joining game"));
      }
    }
  };

  const handlePasswordSubmit = (password) => {
    if (selectedGame) {
      joinGame(selectedGame.id, username, password)
        .then((res) => {
          setPlayerId(res.player_id);
          navigate(`/games/lobby/${selectedGame.id}/${res.player_id}`);

        })
        .catch((err) => setError(err));
    }
    // setIsPasswordModalOpen(false);
  };

  useGameSocket(fetchGames, currentPage, isFiltering, formData);

  useEffect(() => {
    fetchGames(currentPage, formData);
  }, [currentPage, isFiltering]);

  return (
    <div className="w-full h-screen flex flex-col justify-center items-center bg-zinc-950 text-white">
      <h1 className="w-full text-6xl text-center mb-10 text-white">Lista de partidas</h1>

      <div className="sm:w-3/4 md:w-[700px] lg:1/2">
        <div className="flex justify-between mb-4 items-center">
          {/* Create Game Button */}
          <button
            onClick={handleCreateGame}
            className="text-white py-2 px-4 text-4xl rounded hover:text-gray-500 transition-all duration-200 flex items-center"
          >
            <FaPlus size={30} className="mr-2" />
          </button>

          <div className="flex space-x-4 items-center">
            {/* Filter Button */}
            <PageFilter
              setGames={setGames}
              setTotalPages={setTotalPages}
              setIsFiltering={setIsFiltering}
              formData={formData}
              setFormData={setFormData}
              fetchGames={fetchGames}
            />

            {/* Undo Filter Button */}
            <button
              disabled={!isFiltering}
              onClick={handleRemoveFilter}
              className={`py-2 px-4 rounded transition-all duration-200 flex items-center ${
                isFiltering
                  ? 'text-red-500 hover:text-red-600'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              <MdOutlineCleaningServices size={30} className="mr-2" />
            </button>
          </div>

          {/* Join Game Button */}
          <button
            onClick={handleJoinGame}
            disabled={!selectedGame}
            className={`py-2 px-4 rounded transition-all duration-200 flex items-center ${
              selectedGame
                ? 'text-green-600 hover:text-green-700'
                : 'text-gray-400 cursor-not-allowed'
            }`}
          >
            <FaPlay size={30} className="mr-2" />
          </button>
        </div>

        <GamesList
          games={games}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          totalPages={totalPages}
          loading={loading}
          selectedGame={selectedGame}
          setSelectedGame={setSelectedGame}
        />
      </div>

      {/* Password Modal */}
      <PasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => {
          setIsPasswordModalOpen(false);
          setError('')
        }}
        onSubmit={handlePasswordSubmit}
        error={error}
      />
    </div>
  );
};

export default Games;
