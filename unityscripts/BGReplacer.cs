using UnityEngine;

public class BGReplacer : MonoBehaviour {

	public string prefix;
	public int numberOfBackgrounds;
	
	void Update () {
		if (Screenshotter.backgroundNeedsUpdate) {
			int randomInt = Random.Range (1, numberOfBackgrounds);
			Resources.UnloadAsset (GetComponent<Renderer> ().material.mainTexture);
			Texture backgroundImage = (Texture)Resources.Load (prefix + randomInt);
			this.GetComponent<Renderer> ().material.mainTexture = backgroundImage;

			Screenshotter.backgroundNeedsUpdate = false;
		}
	}
}
