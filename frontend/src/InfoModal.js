function InfoModal({ onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>About</h2>
        <p>Hello! This is my Fantasy Football Draft Assistant, that uses custom logic and AI explanations to help you draft the best fantasy team. When you are drafting a team, you can use this tool to track the draft, and input how the draft is going, so the Assistant can recommend the best choice for your team.</p>

        <h3>Scoring</h3>
        <p>The scoring is based on 4 categories that fit into one overall score:</p>
        <ul>
            <p><strong>Base Score:</strong> The ranking given by Sleeper</p>
            <p><strong>Potential Score:</strong> Aims to project a player's peak based on their age, increase/decrease in perfomance, starting status, targets, snaps, and experience</p>
            <p><strong>Sleeper Score:</strong> Evaluates if a player is a "sleeper" — being undervalued compared to their potential</p>
            <p><strong>Need Score:</strong> How much your roster needs that position</p>
            <p><strong>Overall Score:</strong> The combined score of all of these metrics</p>
        </ul>

        <h3>Upcoming Features</h3>
        <ul>
            <p><strong>Coming soon:</strong> Connecting to the Sleeper Fantasy App for automatic pick tracking</p>
            <p><strong>Further along:</strong> Connecting to ESPN, Yahoo, and NFL Fantasy</p>
            <p><strong>Always ongoing:</strong> Tweaking score metrics for the most accurate recommendations, improving UI, implementing suggestions from users</p>
        </ul>
        <button onClick={onClose}>Got It</button>
      </div>
    </div>
  );
}

export default InfoModal;